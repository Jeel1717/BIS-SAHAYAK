export type ChatMode = "consumer" | "industry";

export interface Citation {
  number: number;
  title: string;
  source_url: string;
  clause_number: string | null;
  page_number: number | null;
}

export interface AssessmentData {
  productIdentified: string;
  applicableStandard: string;
  standardTitle?: string;
  certificationPathway: string;
  procedure: string;
  evidenceSource: string;
  evidenceItem?: string;
  sourceUrl?: string;
  nextStep: string;
  foundInformation: boolean;
  rawAnswer: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  foundInformation?: boolean;
  timestamp: Date;
  assessment?: AssessmentData;
}

export interface ChatApiResponse {
  session_id: string;
  answer: string;
  citations: Citation[];
  found_information: boolean;
}

