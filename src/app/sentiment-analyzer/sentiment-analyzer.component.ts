import { Component } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { HttpClient } from "@angular/common/http";

interface SentimentResponse {
  text: string;
  sentiment: string;
}

@Component({
  selector: "app-sentiment-analyzer",
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="sentiment-analyzer">
      <h2>✍️ Enter your text here</h2>

      <div class="form-group">
        <label for="textInput">Text to analyze:</label>
        <textarea
          id="textInput"
          [(ngModel)]="inputText"
          class="form-control"
          rows="4"
          placeholder="Example: I love this movie! It's amazing..."
          [disabled]="isLoading"
        >
        </textarea>
      </div>

      <div class="form-group">
        <button
          class="btn"
          (click)="analyzeSentiment()"
          [disabled]="!inputText.trim() || isLoading"
        >
          {{ isLoading ? "Analyzing..." : "🔍 Analyze Sentiment" }}
        </button>
      </div>

      <div *ngIf="isLoading" class="loading">
        <div class="spinner"></div>
        <p>Analyzing your text...</p>
      </div>

      <div *ngIf="error" class="alert alert-danger">
        <strong>Error:</strong> {{ error }}
      </div>

      <div *ngIf="result" class="result" [ngClass]="getSentimentClass()">
        <h2>{{ result.sentiment }}</h2>
        <p><strong>Text:</strong> "{{ result.text }}"</p>
      </div>

      <div class="examples">
        <h3>💡 Try these examples:</h3>
        <div class="example-buttons">
          <button
            *ngFor="let example of examples"
            class="btn example-btn"
            (click)="setExample(example)"
            [disabled]="isLoading"
          >
            {{ example }}
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      .sentiment-analyzer {
        text-align: center;
      }

      .sentiment-analyzer h2 {
        color: #667eea;
        margin-bottom: 30px;
      }

      .examples {
        margin-top: 40px;
        text-align: left;
      }

      .examples h3 {
        color: #555;
        margin-bottom: 15px;
      }

      .example-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }

      .example-btn {
        font-size: 14px;
        padding: 8px 16px;
        background: #f8f9fa;
        color: #333;
        border: 1px solid #dee2e6;
      }

      .example-btn:hover {
        background: #e9ecef;
        transform: none;
        box-shadow: none;
      }

      .result.positive h2 {
        color: #28a745;
      }

      .result.negative h2 {
        color: #dc3545;
      }
    `,
  ],
})
export class SentimentAnalyzerComponent {
  inputText = "";
  result: SentimentResponse | null = null;
  error = "";
  isLoading = false;

  examples = [
    "I love this movie!",
    "This is amazing!",
    "I hate this",
    "This was terrible",
    "What a great day!",
    "Worst experience ever",
  ];

  private apiUrl = "http://127.0.0.1:8000";

  constructor(private http: HttpClient) {}

  analyzeSentiment() {
    if (!this.inputText.trim()) return;

    this.isLoading = true;
    this.error = "";
    this.result = null;

    const requestBody = { text: this.inputText };

    console.log("Sending request to:", `${this.apiUrl}/predict`);
    console.log("Request body:", requestBody);

    this.http
      .post<SentimentResponse>(`${this.apiUrl}/predict`, requestBody, {
        headers: {
          "Content-Type": "application/json",
        },
      })
      .subscribe({
        next: (response) => {
          console.log("Response received:", response);
          this.result = response;
          this.isLoading = false;
        },
        error: (error) => {
          console.error("API Error:", error);
          console.error("Error status:", error.status);
          console.error("Error message:", error.message);
          this.error =
            error.error?.detail ||
            error.message ||
            "An error occurred while analyzing the text.";
          this.isLoading = false;
        },
      });
  }

  setExample(example: string) {
    this.inputText = example;
    this.error = "";
    this.result = null;
  }

  getSentimentClass(): string {
    if (!this.result) return "";
    return this.result.sentiment.includes("Positive") ? "positive" : "negative";
  }
}
