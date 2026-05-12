import { CommonModule } from "@angular/common";
import { Component, Input } from "@angular/core";

import { SentimentResponse } from "./sentiment-api.service";

@Component({
  selector: "app-sentiment-result",
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="result" [ngClass]="result.sentiment">
      <div class="result-header">
        <span class="badge">{{ result.label }}</span>
        <span
          *ngIf="result.confidence !== null && result.confidence !== undefined"
          class="confidence"
        >
          {{ formatPercent(result.confidence) }} confidence
        </span>
      </div>

      <div
        *ngIf="result.confidence !== null && result.confidence !== undefined"
        class="confidence-bar"
        aria-label="Prediction confidence"
        role="meter"
        aria-valuemin="0"
        aria-valuemax="100"
        [attr.aria-valuenow]="percentValue(result.confidence)"
      >
        <div class="confidence-fill" [style.width]="formatPercent(result.confidence)"></div>
      </div>

      <div *ngIf="result.probabilities" class="probabilities">
        <span>Positive: {{ formatPercent(result.probabilities.positive) }}</span>
        <span>Negative: {{ formatPercent(result.probabilities.negative) }}</span>
      </div>

      <p><strong>Text:</strong> "{{ result.text }}"</p>
    </div>
  `,
  styles: [
    `
      .result {
        text-align: left;
        margin: 30px 0;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        background: var(--soft-bg);
      }

      .result.positive {
        border-color: #b7e4c7;
      }

      .result.negative {
        border-color: #f5c2c7;
      }

      .result-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 14px;
      }

      .badge {
        display: inline-flex;
        border-radius: 999px;
        padding: 6px 12px;
        font-weight: 700;
      }

      .positive .badge {
        color: #155724;
        background: #d4edda;
      }

      .negative .badge {
        color: #721c24;
        background: #f8d7da;
      }

      .confidence {
        color: var(--muted-color);
        font-weight: 600;
      }

      .confidence-bar {
        height: 10px;
        overflow: hidden;
        border-radius: 999px;
        background: #e9ecef;
        margin-bottom: 12px;
      }

      .confidence-fill {
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      .probabilities {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin: 10px 0;
        color: var(--muted-color);
      }

      @media (max-width: 600px) {
        .result-header {
          align-items: flex-start;
          flex-direction: column;
        }
      }
    `,
  ],
})
export class SentimentResultComponent {
  @Input({ required: true }) result!: SentimentResponse;

  formatPercent(value: number): string {
    return `${this.percentValue(value)}%`;
  }

  percentValue(value: number): number {
    return Math.round(value * 100);
  }
}
