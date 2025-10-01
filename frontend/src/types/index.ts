export interface Topic {
  id: string;
  name: string;
  category: string;
  base_score: number;
  date_added: string;
  last_seen: string | null;
  attempts: number;
  successes: number;
  rec_scores: number[];
  rec_score_avg: number;
  success_rate: number;
  last_seen_formatted: string;
  date_added_formatted: string;
}

export interface Question {
  rec_id: string;
  set_id: string;
  rec_no: number;
  topic_id: string;
  topic_name: string;
  category: string;
  question_type: 'mcq' | 'code' | 'blank';
  question_text: string;
  user_answer: string | null;
  is_correct: boolean | null;
  difficulty_rating: 'easy' | 'medium' | 'hard' | null;
}

export interface Assessment {
  set_id: string;
  questions: Question[];
}

export interface AssessmentResult {
  rec_no: number;
  is_correct: boolean;
  difficulty_rating: 'easy' | 'medium' | 'hard';
}

export interface MCQOptions {
  A: string;
  B: string;
  C: string;
  D: string;
  correct: string;
}

export interface CodeVerification {
  result: 'YES' | 'NO';
  feedback: string;
  suggestions: string;
}

export interface Stats {
  overall: {
    total_topics: number;
    total_attempts: number;
    total_successes: number;
    success_rate: number;
    total_sets: number;
  };
  categories: {
    [category: string]: {
      count: number;
      attempts: number;
      successes: number;
      success_rate: number;
      avg_difficulty: number;
    };
  };
  topics: Topic[];
}