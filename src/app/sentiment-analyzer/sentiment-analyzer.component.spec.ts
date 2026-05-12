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
  });

  it("posts text to the predict endpoint and stores the result", () => {
    component.inputText = "I love this movie";

    component.analyzeSentiment();

    const request = http.expectOne("/predict");
    expect(request.request.method).toBe("POST");
    expect(request.request.body).toEqual({ text: "I love this movie" });

    request.flush({
      text: "I love this movie",
      sentiment: "positive",
      label: "Positive",
      confidence: 0.9,
      probabilities: { positive: 0.9, negative: 0.1 },
    });

    expect(component.result?.sentiment).toBe("positive");
    expect(component.getSentimentClass()).toBe("positive");
    expect(component.formatPercent(0.9)).toBe("90%");
    expect(component.isLoading).toBeFalse();
  });
});
