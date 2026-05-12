import { provideHttpClient } from "@angular/common/http";
import {
  HttpTestingController,
  provideHttpClientTesting,
} from "@angular/common/http/testing";
import { ComponentFixture, TestBed } from "@angular/core/testing";

import { SentimentAnalyzerComponent } from "./sentiment-analyzer.component";

describe("SentimentAnalyzerComponent", () => {
  let fixture: ComponentFixture<SentimentAnalyzerComponent>;
  let component: SentimentAnalyzerComponent;
  let http: HttpTestingController;

  beforeEach(async () => {
    localStorage.clear();

    await TestBed.configureTestingModule({
      imports: [SentimentAnalyzerComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(SentimentAnalyzerComponent);
    component = fixture.componentInstance;
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
    localStorage.clear();
    document.body.classList.remove("dark-theme");
  });

  function flushStartup(modelAvailable = true): void {
    const healthRequest = http.expectOne("/api/v1/health");
    healthRequest.flush({ status: "ok", model_available: modelAvailable });

    const modelInfoRequest = http.expectOne("/api/v1/model-info");
    modelInfoRequest.flush({
      model_available: modelAvailable,
      metadata: modelAvailable
        ? {
            model_type: "LogisticRegression",
            vectorizer: "TfidfVectorizer",
            accuracy: 0.9,
            dataset_size: 50,
          }
        : null,
    });
  }

  it("checks health and posts text to the predict endpoint", () => {
    fixture.detectChanges();
    flushStartup();

    component.inputText = "I love this movie";
    component.analyzeSentiment();

    const predictRequest = http.expectOne("/api/v1/predict");
    expect(predictRequest.request.method).toBe("POST");
    expect(predictRequest.request.body).toEqual({ text: "I love this movie" });

    predictRequest.flush({
      text: "I love this movie",
      sentiment: "positive",
      label: "Positive",
      confidence: 0.9,
      probabilities: { positive: 0.9, negative: 0.1 },
    });

    expect(component.result?.sentiment).toBe("positive");
    expect(component.history.length).toBe(1);
    expect(component.formatPercent(0.9)).toBe("90%");
    expect(component.isLoading).toBeFalse();
  });

  it("disables analysis when the model is unavailable", () => {
    fixture.detectChanges();
    flushStartup(false);

    component.inputText = "I love this movie";
    component.analyzeSentiment();

    expect(component.healthState).toBe("unavailable");
    expect(component.result).toBeNull();
  });

  it("maps rate limit errors to a helpful message", () => {
    fixture.detectChanges();
    flushStartup();

    component.inputText = "I love this movie";
    component.analyzeSentiment();

    http.expectOne("/api/v1/predict").flush(
      { error: { code: "RATE_LIMIT_EXCEEDED", message: "Too many requests." } },
      { status: 429, statusText: "Too Many Requests" },
    );

    expect(component.error).toBe("Too many requests.");
    expect(component.isLoading).toBeFalse();
  });

  it("analyzes a batch and toggles dark mode", () => {
    fixture.detectChanges();
    flushStartup();

    component.batchInput = "I love this app\nThis was bad";
    component.analyzeBatch();

    const batchRequest = http.expectOne("/api/v1/predict/batch");
    expect(batchRequest.request.body).toEqual({
      texts: ["I love this app", "This was bad"],
    });
    batchRequest.flush({
      results: [
        {
          text: "I love this app",
          sentiment: "positive",
          label: "Positive",
          confidence: 0.9,
          probabilities: { positive: 0.9, negative: 0.1 },
        },
        {
          text: "This was bad",
          sentiment: "negative",
          label: "Negative",
          confidence: 0.8,
          probabilities: { positive: 0.2, negative: 0.8 },
        },
      ],
    });

    expect(component.batchResults.length).toBe(2);
    expect(component.history.length).toBe(2);

    component.toggleTheme();
    expect(document.body.classList.contains("dark-theme")).toBeTrue();
  });
});
