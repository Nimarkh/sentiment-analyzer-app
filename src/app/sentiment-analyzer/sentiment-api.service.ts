import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";

export interface HealthResponse {
  status: "ok";
  model_available: boolean;
}

export interface SentimentResponse {
  text: string;
  sentiment: "positive" | "negative";
  label: string;
  confidence?: number | null;
  probabilities?: {
    positive: number;
    negative: number;
  } | null;
}

export interface BatchSentimentResponse {
  results: SentimentResponse[];
}

export interface ModelInfoResponse {
  model_available: boolean;
  metadata: {
    model_type?: string;
    vectorizer?: string;
    accuracy?: number;
    dataset_size?: number;
    trained_at?: string;
  } | null;
}

@Injectable({ providedIn: "root" })
export class SentimentApiService {
  private readonly baseUrl = "/api/v1";

  constructor(private http: HttpClient) {}

  health(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(`${this.baseUrl}/health`);
  }

  predict(text: string): Observable<SentimentResponse> {
    return this.http.post<SentimentResponse>(`${this.baseUrl}/predict`, { text });
  }

  predictBatch(texts: string[]): Observable<BatchSentimentResponse> {
    return this.http.post<BatchSentimentResponse>(`${this.baseUrl}/predict/batch`, { texts });
  }

  modelInfo(): Observable<ModelInfoResponse> {
    return this.http.get<ModelInfoResponse>(`${this.baseUrl}/model-info`);
  }
}
