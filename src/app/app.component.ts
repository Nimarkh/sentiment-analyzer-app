import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { SentimentAnalyzerComponent } from './sentiment-analyzer/sentiment-analyzer.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, SentimentAnalyzerComponent],
  template: `
    <div class="container">
      <div class="header">
        <h1>🧠 Sentiment Analyzer</h1>
        <p>Analyze the sentiment of any text using AI</p>
      </div>
      
      <div class="card">
        <app-sentiment-analyzer></app-sentiment-analyzer>
      </div>
      
      <div class="footer">
        <p>Made with ❤️ using Angular, FastAPI, and scikit-learn</p>
      </div>
    </div>
  `,
  styles: []
})
export class AppComponent {
  title = 'sentiment-analyzer';
}
