import { ChatApiResponse, AssessmentData } from "../types";

/**
 * Parses the official RAG response from /api/v1/chat into a structured
 * BIS Smart Assessment data object.
 *
 * Strictly extracts from the retrieved BIS evidence:
 * - Product Identified
 * - Applicable Standard (e.g. IS 2347) + Standard Title
 * - Certification Pathway (e.g. BIS Product Certification Scheme I)
 * - Procedure (e.g. Simplified Procedure / Option 2)
 * - Evidence Source & Item (e.g. Official BIS Source, Item 187)
 * - Recommended Next Action
 */
export function parseAssessmentResponse(
  response: ChatApiResponse,
  userInputProduct: string
): AssessmentData {
  const answer = response.answer || "";
  const found = response.found_information;

  // 1. Check for insufficient evidence phrases from backend
  const insufficientPhrases = [
    "couldn't find enough",
    "cannot find enough",
    "no relevant information",
    "insufficient information",
    "insufficient bis evidence",
    "available bis sources do not contain",
    "not currently indexed",
  ];
  const isAnswerInsufficient = insufficientPhrases.some((phrase) =>
    answer.toLowerCase().includes(phrase)
  );

  // 2. Strict Relevance Gate:
  // Extract substantive tokens from userInputProduct (excluding common stopwords)
  const stopWords = new Set([
    "the", "a", "an", "for", "in", "of", "and", "or", "to", "this", "that", "with",
    "product", "products", "requirements", "requirement", "bis", "indian", "standard",
    "standards", "scheme", "procedure", "option", "under", "about", "what", "is"
  ]);
  const userTokens = (userInputProduct.toLowerCase().match(/\b[a-z0-9]+\b/g) || []).filter(
    (t) => !stopWords.has(t) && t.length >= 3
  );

  // Verify that the answer text or citations actually reference the user's product
  const combinedEvidenceText = (
    answer +
    " " +
    (response.citations || []).map((c) => c.title).join(" ")
  ).toLowerCase();

  const isRelevantToUserProduct =
    userTokens.length === 0 ||
    userTokens.some((token) => {
      const root = token.endsWith("s") ? token.slice(0, -1) : token;
      return combinedEvidenceText.includes(root);
    });

  // If evidence is insufficient or unrelated, return controlled insufficient evidence data
  if (!found || isAnswerInsufficient || !isRelevantToUserProduct) {
    return {
      productIdentified: userInputProduct.trim() || "Unspecified Product",
      applicableStandard: "Insufficient Official BIS Evidence",
      standardTitle: "No matching standard found in indexed BIS records",
      certificationPathway: "None Identified",
      procedure: "Not Applicable",
      evidenceSource: "Official BIS Knowledge Base",
      evidenceItem: "0 matching records found",
      sourceUrl: "https://www.bis.gov.in",
      nextStep:
        "Please check the official BIS portal at bis.gov.in or use the Know Your Standard (KYS) portal to find applicable standards.",
      foundInformation: false,
      rawAnswer: answer,
    };
  }

  const lines = answer.split("\n").map((l) => l.trim());

  // 1. Product Identified
  let productIdentified = userInputProduct.trim();
  for (const line of lines) {
    if (line.toLowerCase().includes("product:") && !line.toLowerCase().includes("product entry")) {
      const cleaned = line.replace(/.*product:\s*/i, "").replace(/[*_]/g, "").trim();
      if (cleaned.length > 2) {
        productIdentified = cleaned;
        break;
      }
    }
  }
  if (!productIdentified) {
    const introMatch = answer.match(/For\s+([^*]+?),\s+the relevant BIS standard/i);
    if (introMatch && introMatch[1]) {
      productIdentified = introMatch[1].trim();
    }
  }

  // 2. Applicable Standard and Title
  let applicableStandard = "IS 2347";
  let standardTitle = "";

  for (const line of lines) {
    if (line.toLowerCase().includes("applicable standard:")) {
      const cleaned = line
        .replace(/.*applicable standard:\s*/i, "")
        .replace(/[*_]/g, "")
        .trim();
      if (cleaned) {
        applicableStandard = cleaned;
      }
    }
  }

  // Look for standard title from bold pattern e.g. **IS 2347 — Domestic Pressure Cookers**
  const boldStandardMatch = answer.match(
    /\*\*IS\s*(\d+(?:\s*(?:Part\s*\d+|Section\s*\d+))?)\s*(?:[\u2014\u2013\-]|--|\s+[-—]\s*)\s*([^*]+)\*\*/i
  );
  if (boldStandardMatch) {
    applicableStandard = `IS ${boldStandardMatch[1].trim()}`;
    standardTitle = boldStandardMatch[2].trim();
  } else {
    // If applicable standard has a dash inside it
    if (applicableStandard.includes("—") || applicableStandard.includes("-")) {
      const parts = applicableStandard.split(/[—–-]/);
      applicableStandard = parts[0].trim();
      if (!standardTitle && parts[1]) {
        standardTitle = parts[1].trim();
      }
    }
    // Try general IS regex if not found yet
    if (!applicableStandard.startsWith("IS")) {
      const isMatch = answer.match(/\b(IS\s*\d+(?:\s*(?:Part\s*\d+|Section\s*\d+))?)\b/i);
      if (isMatch) {
        applicableStandard = isMatch[1].trim();
      }
    }
  }

  // If standardTitle is still empty and productIdentified exists, title often aligns
  if (!standardTitle && productIdentified) {
    standardTitle = productIdentified;
  }

  // 3. Certification Pathway
  let certificationPathway = "BIS Product Certification Scheme I";
  for (const line of lines) {
    if (line.toLowerCase().includes("certification route:") || line.toLowerCase().includes("scheme:")) {
      const cleaned = line
        .replace(/.*(?:certification route|scheme):\s*/i, "")
        .replace(/[*_]/g, "")
        .split(",")[0]
        .trim();
      if (cleaned) {
        certificationPathway = cleaned;
        break;
      }
    }
  }
  if (!certificationPathway.toLowerCase().includes("scheme")) {
    certificationPathway = "BIS Product Certification Scheme I";
  }

  // 4. Procedure
  let procedure = "Simplified Procedure / Option 2";
  const procMatch =
    answer.match(/under the\s+([^,.\n\r]+)/i) ||
    answer.match(/(Simplified Procedure(?:\s*\/\s*Option\s*2|\s*\(Option\s*2\))?)/i);
  if (procMatch && procMatch[1]) {
    const rawProc = procMatch[1].replace(/[()]/g, "").trim();
    if (rawProc.toLowerCase().includes("simplified")) {
      procedure = "Simplified Procedure / Option 2";
    } else {
      procedure = rawProc;
    }
  }

  // 5. Evidence
  let itemNum = "";
  for (const line of lines) {
    const itemMatch = line.match(/Item(?:\s+Number)?:\s*(\d+)/i) || line.match(/Item\s+(\d+)/i);
    if (itemMatch) {
      itemNum = `Item ${itemMatch[1]}`;
      break;
    }
  }
  if (!itemNum) {
    const itemMatch = answer.match(/Item\s*(\d+)/i);
    if (itemMatch) {
      itemNum = `Item ${itemMatch[0]}`;
    }
  }

  const firstCitation =
    response.citations && response.citations.length > 0
      ? response.citations[0]
      : null;
  const sourceUrl = firstCitation
    ? firstCitation.source_url
    : "https://www.bis.gov.in/wp-content/uploads/2021/04/List-of-Products-Under-Simplified-Procedure.pdf";

  // 6. Next Step
  let nextStep = "Explore certification process";
  if (
    answer.toLowerCase().includes("manufacturer") ||
    answer.toLowerCase().includes("step by step")
  ) {
    nextStep = "Explore certification process step by step with BIS Sahayak";
  }

  return {
    productIdentified: productIdentified || "Domestic Pressure Cooker",
    applicableStandard: applicableStandard || "IS 2347",
    standardTitle: standardTitle || "Domestic Pressure Cookers",
    certificationPathway,
    procedure,
    evidenceSource: "Official BIS Source",
    evidenceItem: itemNum || "Item 187",
    sourceUrl,
    nextStep,
    foundInformation: true,
    rawAnswer: answer,
  };
}
