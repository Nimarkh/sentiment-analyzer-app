import { CommonModule } from "@angular/common";
import { Component, OnInit } from "@angular/core";
import { FormsModule } from "@angular/forms";

import {
  HealthResponse,
  ModelInfoResponse,
  SentimentApiService,
  SentimentResponse,
} from "./sentiment-api.service";
import { SentimentResultComponent } from "./sentiment-result.component";

type HealthState = "checking" | "ready" | "unavailable";

@Component({
  selector: "app-sentiment-analyzer",
  standalone: true,
  imports: [CommonModule, FormsModule, SentimentResultComponent],
  template: `
    <div class="sentiment-analyzer">
      <div class="top-actions">
        <button class="link-button" type="button" (click)="toggleTheme()">
          {{ isDarkTheme ? "Light mode" : "Dark mode" }}
        </button>
        <button
          class="link-button"
          type="button"
          (click)="exportHistory()"
          [disabled]="!history.length"
        >
          Export history
        </button>
      </div>

      <div class="status" [ngClass]="healthState" role="status" aria-live="polite">
        <span>{{ healthMessage }}</span>
        <button
          *ngIf="healthState === 'unavailable'"
          class="link-button"
          type="button"
          (click)="checkHealth()"
        >
          Retry
        </button>
      </div>

      <div *ngIf="modelInfo?.metadata" class="model-info">
        <strong>Model:</strong>
        {{ modelInfo?.metadata?.model_type }} +
        {{ modelInfo?.metadata?.vectorizer }}
        <span *ngIf="modelInfo?.metadata?.accuracy !== undefined">
          | Accuracy: {{ formatPercent(modelInfo!.metadata!.accuracy!) }}
        </span>
        <span *ngIf="modelInfo?.metadata?.dataset_size">
          | Dataset: {{ modelInfo?.metadata?.dataset_size }} samples
        </span>
      </div>

      <h2>Enter your text</h2>

      <div class="form-group">
        <label for="textInput">Text to analyze:</label>
        <textarea
          id="textInput"
          [(ngModel)]="inputText"
          class="form-control"
          rows="4"
          maxlength="5000"
          placeholder="Example: I love this movie! It's amazing..."
          [disabled]="isLoading"
        ></textarea>
        <div class="character-count">{{ inputText.length }}/5000</div>
      </div>

      <div class="actions">
        <button
          class="btn"
          type="button"
          (click)="analyzeSentiment()"
          [disabled]="!canAnalyze"
        >
          {{ isLoading ? "Analyzing..." : "Analyze Sentiment" }}
        </button>
        <button
          class="btn secondary-btn"
          type="button"
          (click)="reset()"
          [disabled]="isLoading && !inputText && !result && !error"
        >
          Reset
        </button>
      </div>

      <div *ngIf="isLoading" class="loading" role="status" aria-live="polite">
        <div class="spinner"></div>
        <p>Analyzing your text...</p>
      </div>

      <div *ngIf="error" class="alert alert-danger" role="alert">
        <strong>Error:</strong> {{ error }}
      </div>

      <app-sentiment-result
        *ngIf="result"
        [result]="result"
      ></app-sentiment-result>

      <div class="examples">
        <h3>Examples</h3>
        <div class="example-buttons">
          <button
            *ngFor="let example of examples"
            class="btn example-btn"
            type="button"
            (click)="setExample(example)"
            [disabled]="isLoading"
          >
            {{ example }}
          </button>
        </div>
      </div>

      <div class="batch-panel">
        <h3>Compare multiple texts</h3>
        <p>Enter one text per line and analyze up to 10 items at once.</p>
        <textarea
          [(ngModel)]="batchInput"
          class="form-control"
          rows="4"
          placeholder="I love this app&#10;This was frustrating"
          [disabled]="isBatchLoading"
        ></textarea>
        <button
          class="btn"
          type="button"
          (click)="analyzeBatch()"
          [disabled]="!canAnalyzeBatch"
        >
          {{ isBatchLoading ? "Comparing..." : "Compare texts" }}
        </button>
        <div *ngIf="batchResults.length" class="batch-results">
          <app-sentiment-result
            *ngFor="let item of batchResults"
            [result]="item"
          ></app-sentiment-result>
        </div>
      </div>

      <div *ngIf="history.length" class="history">
        <div class="history-header">
          <h3>Recent analyses</h3>
          <button class="link-button" type="button" (click)="clearHistory()">
            Clear
          </button>
        </div>
        <button
          *ngFor="let item of history"
          class="history-item"
          type="button"
          (click)="restoreHistory(item)"
        >
          <span class="history-label" [ngClass]="item.sentiment">{{ item.label }}</span>
          <span class="history-text">{{ item.text }}</span>
          <span
            *ngIf="item.confidence !== null && item.confidence !== undefined"
            class="history-confidence"
          >
            {{ formatPercent(item.confidence) }}
          </span>
        </button>
      </div>
    </div>
  `,
  styles: [
    `
      .sentiment-analyzer {
        text-align: center;
      }

      .top-actions {
        display: flex;
        justify-content: flex-end;
        gap: 16px;
        margin-bottom: 16px;
      }

      .sentiment-analyzer h2 {
        color: #667eea;
        margin: 24px 0 30px;
      }

      .status {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        padding: 10px 12px;
        border-radius: 8px;
        font-weight: 600;
      }

      .model-info {
        margin-top: 12px;
        padding: 10px 12px;
        border-radius: 8px;
        color: var(--muted-color);
        background: var(--soft-bg);
      }

      .status.checking {
        color: #856404;
        background: #fff3cd;
      }

      .status.ready {
        color: #155724;
        background: #d4edda;
      }

      .status.unavailable {
        color: #721c24;
        background: #f8d7da;
      }

      .character-count {
        text-align: right;
        margin-top: 6px;
        color: #666;
        font-size: 13px;
      }

      .actions {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin: 20px 0;
      }

      .secondary-btn {
        color: #333;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
      }

      .link-button {
        border: none;
        background: transparent;
        color: #667eea;
        cursor: pointer;
        font-weight: 700;
        text-decoration: underline;
      }

      .examples,
      .batch-panel,
      .history {
        margin-top: 40px;
        text-align: left;
      }

      .examples h3,
      .batch-panel h3,
      .history h3 {
        color: var(--muted-color);
        margin-bottom: 15px;
      }

      .batch-panel p {
        margin-bottom: 12px;
        color: var(--muted-color);
      }

      .batch-panel .btn {
        margin-top: 12px;
      }

      .batch-results {
        margin-top: 20px;
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

      .example-btn:hover,
      .secondary-btn:hover {
        background: #e9ecef;
        transform: none;
        box-shadow: none;
      }

      .history-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }

      .history-item {
        width: 100%;
        display: grid;
        grid-template-columns: auto 1fr auto;
        gap: 12px;
        align-items: center;
        margin-bottom: 10px;
        padding: 12px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-color);
        background: var(--card-bg);
        cursor: pointer;
        text-align: left;
      }

      .history-label {
        border-radius: 999px;
        padding: 4px 8px;
        font-size: 12px;
        font-weight: 700;
      }

      .history-label.positive {
        color: #155724;
        background: #d4edda;
      }

      .history-label.negative {
        color: #721c24;
        background: #f8d7da;
      }

      .history-text {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .history-confidence {
        color: var(--muted-color);
        font-weight: 700;
      }

      @media (max-width: 600px) {
        .actions,
        .status,
        .top-actions {
          align-items: stretch;
          flex-direction: column;
        }

        .btn {
          width: 100%;
        }

        .history-item {
          grid-template-columns: 1fr;
        }

        .history-text {
          white-space: normal;
        }
      }
    `,
  ],
})
export class SentimentAnalyzerComponent implements OnInit {
  inputText = "";
  result: SentimentResponse | null = null;
  error = "";
  isLoading = false;
  isBatchLoading = false;
  isDarkTheme = false;
  healthState: HealthState = "checking";
  healthMessage = "Checking model status...";
  history: SentimentResponse[] = [];
  batchInput = "";
  batchResults: SentimentResponse[] = [];
  modelInfo: ModelInfoResponse | null = null;

  readonly examples = [
    "I love this movie!",
    "This is amazing!",
    "I hate this",
    "This was terrible",
    "What a great day!",
    "Worst experience ever",
  ];

  private readonly maxHistoryItems = 5;
  private readonly historyStorageKey = "sentiment-history";
  private readonly themeStorageKey = "sentiment-theme";

  constructor(private api: SentimentApiService) {}

  ngOnInit(): void {
    this.history = this.loadHistory();
    this.isDarkTheme = localStorage.getItem(this.themeStorageKey) === "dark";
    this.applyTheme();
    this.checkHealth();
    this.loadModelInfo();
  }

  get canAnalyze(): boolean {
    return Boolean(this.inputText.trim()) && !this.isLoading && this.healthState === "ready";
  }

  get canAnalyzeBatch(): boolean {
    return (
      this.getBatchTexts().length > 0 &&
      !this.isBatchLoading &&
      this.healthState === "ready"
    );
  }

  checkHealth(): void {
    this.healthState = "checking";
    this.healthMessage = "Checking model status...";

    this.api.health().subscribe({
      next: (response: HealthResponse) => {
        if (response.model_available) {
          this.healthState = "ready";
          this.healthMessage = "Model is ready.";
          return;
        }

        this.healthState = "unavailable";
        this.healthMessage = "Model is not ready. Run setup_model.py first.";
      },
      error: () => {
        this.healthState = "unavailable";
        this.healthMessage = "Backend is unavailable. Make sure FastAPI is running.";
      },
    });
  }

  analyzeSentiment(): void {
    if (!this.canAnalyze) return;

    const text = this.inputText.trim();
    this.isLoading = true;
    this.error = "";
    this.result = null;

    this.api.predict(text).subscribe({
      next: (response) => {
        this.result = response;
        this.addToHistory(response);
        this.isLoading = false;
      },
      error: (error) => {
        this.error = this.getErrorMessage(error);
        this.isLoading = false;
      },
    });
  }

  analyzeBatch(): void {
    if (!this.canAnalyzeBatch) return;

    const texts = this.getBatchTexts();
    this.isBatchLoading = true;
    this.error = "";
    this.batchResults = [];

    this.api.predictBatch(texts).subscribe({
      next: (response) => {
        this.batchResults = response.results;
        response.results.forEach((item) => this.addToHistory(item));
        this.isBatchLoading = false;
      },
      error: (error) => {
        this.error = this.getErrorMessage(error);
        this.isBatchLoading = false;
      },
    });
  }

  setExample(example: string): void {
    this.inputText = example;
    this.error = "";
    this.result = null;
  }

  reset(): void {
    this.inputText = "";
    this.error = "";
    this.result = null;
  }

  toggleTheme(): void {
    this.isDarkTheme = !this.isDarkTheme;
    localStorage.setItem(this.themeStorageKey, this.isDarkTheme ? "dark" : "light");
    this.applyTheme();
  }

  exportHistory(): void {
    const payload = JSON.stringify(this.history, null, 2);
    const blob = new Blob([payload], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "sentiment-history.json";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  restoreHistory(item: SentimentResponse): void {
    this.inputText = item.text;
    this.result = item;
    this.error = "";
  }

  clearHistory(): void {
    this.history = [];
    localStorage.removeItem(this.historyStorageKey);
  }

  formatPercent(value: number): string {
    return `${Math.round(value * 100)}%`;
  }

  private addToHistory(item: SentimentResponse): void {
    this.history = [
      item,
      ...this.history.filter((historyItem) => historyItem.text !== item.text),
    ].slice(0, this.maxHistoryItems);
    localStorage.setItem(this.historyStorageKey, JSON.stringify(this.history));
  }

  private loadModelInfo(): void {
    this.api.modelInfo().subscribe({
      next: (response) => {
        this.modelInfo = response;
      },
      error: () => {
        this.modelInfo = null;
      },
    });
  }

  private getBatchTexts(): string[] {
    return this.batchInput
      .split("\n")
      .map((text) => text.trim())
      .filter(Boolean)
      .slice(0, 10);
  }

  private applyTheme(): void {
    document.body.classList.toggle("dark-theme", this.isDarkTheme);
  }

  private loadHistory(): SentimentResponse[] {
    try {
      const storedHistory = localStorage.getItem(this.historyStorageKey);
      return storedHistory ? JSON.parse(storedHistory) : [];
    } catch {
      return [];
    }
  }

  private getErrorMessage(error: {
    status?: number;
    error?: { error?: { code?: string; message?: string }; detail?: string };
    message?: string;
  }): string {
    if (error.error?.error?.message) {
      return error.error.error.message;
    }

    if (error.status === 422) {
      return "Please enter valid text before analyzing.";
    }

    if (error.status === 429) {
      return "Too many requests. Please wait a moment and try again.";
    }

    if (error.status === 503) {
      return "The model is not ready. Run setup_model.py and retry.";
    }

    return error.error?.detail || error.message || "An error occurred while analyzing the text.";
  }
}
