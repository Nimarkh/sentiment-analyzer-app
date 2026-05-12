import { Component } from "@angular/core";
import { CommonModule } from "@angular/common";
import { SentimentAnalyzerComponent } from "./sentiment-analyzer/sentiment-analyzer.component";

@Component({
  selector: "app-root",
  standalone: true,
  imports: [CommonModule, SentimentAnalyzerComponent],
  template: `
    <div class="container">
      <div class="header">
        <h1>Sentiment Analyzer</h1>
        <p>Classify text as positive or negative</p>
      </div>

      <div class="card">
        <app-sentiment-analyzer></app-sentiment-analyzer>
      </div>

      <div class="footer">
        <p>Built with Angular, FastAPI, and scikit-learn</p>
      </div>
    </div>
  `,
  styles: [],
})
export class AppComponent {
  title = "sentiment-analyzer";
}

