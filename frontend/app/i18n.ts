export type Language = "en" | "hi";

export interface Translations {
  appName: string;
  modes: {
    consumer: string;
    industry: string;
    consumerDesc: string;
    industryDesc: string;
  };
  header: {
    newChat: string;
    lightMode: string;
    darkMode: string;
    languageSelect: string;
  };
  welcome: {
    title: string;
    subtitle: string;
    tryAsking: string;
  };
  suggestions: {
    consumer: string[];
    industry: string[];
  };
  chat: {
    inputPlaceholder: string;
    sendTooltip: string;
    disclaimer: string;
    groundedBadge: string;
    guidanceBadge: string;
    fallbackHint: string;
    searching: string;
    synthesizing: string;
    sourcesTitle: string;
    verifySource: string;
    retry: string;
    errorConnect: string;
    errorDemand: string;
  };
}

export const translations: Record<Language, Translations> = {
  en: {
    appName: "BIS Sahayak",
    modes: {
      consumer: "Consumer",
      industry: "Industry",
      consumerDesc: "Citizens & Consumers",
      industryDesc: "Standards & Compliance",
    },
    header: {
      newChat: "New Chat",
      lightMode: "Light Mode",
      darkMode: "Dark Mode",
      languageSelect: "Language",
    },
    welcome: {
      title: "BIS Sahayak",
      subtitle: "Your intelligent assistant for BIS standards and services.",
      tryAsking: "Try asking",
    },
    suggestions: {
      consumer: [
        "How do I verify hallmarked gold?",
        "What is HUID?",
        "How can I check if a product is BIS certified?",
      ],
      industry: [
        "How can a manufacturer obtain BIS certification?",
        "How do I find the applicable Indian Standard?",
        "What is the BIS certification process?",
      ],
    },
    chat: {
      inputPlaceholder: "Ask BIS Sahayak anything...",
      sendTooltip: "Send message",
      disclaimer: "BIS Sahayak answers strictly using official Bureau of Indian Standards records.",
      groundedBadge: "Verified BIS Source",
      guidanceBadge: "Public Guidance",
      fallbackHint: "Try asking about BIS certification, hallmarking, HUID, Indian Standards, testing, laboratories, or consumer complaints.",
      searching: "Sahayak is checking the BIS knowledge base…",
      synthesizing: "Formulating grounded answer…",
      sourcesTitle: "Sources",
      verifySource: "Official BIS source",
      retry: "Retry",
      errorConnect: "Something went wrong while processing your request. Please try again.",
      errorDemand: "Service is experiencing high demand. Please try again shortly.",
    },
  },
  hi: {
    appName: "BIS Sahayak",
    modes: {
      consumer: "उपभोक्ता",
      industry: "उद्योग",
      consumerDesc: "नागरिक एवं उपभोक्ता",
      industryDesc: "मानक एवं अनुपालन",
    },
    header: {
      newChat: "नई बातचीत",
      lightMode: "लाइट मोड",
      darkMode: "डार्क मोड",
      languageSelect: "भाषा",
    },
    welcome: {
      title: "BIS Sahayak",
      subtitle: "भारतीय मानकों और बीआईएस सेवाओं के लिए आपकी बुद्धिमत्तापूर्ण मार्गदर्शिका।",
      tryAsking: "यह पूछ कर देखें",
    },
    suggestions: {
      consumer: [
        "हॉलमार्क वाले सोने के आभूषण का सत्यापन कैसे करें?",
        "एचयूआईडी (HUID) क्या है?",
        "कोई उत्पाद बीआईएस प्रमाणित है या नहीं, यह कैसे जांचें?",
      ],
      industry: [
        "एक निर्माता बीआईएस प्रमाणन कैसे प्राप्त कर सकता है?",
        "लागू होने वाला भारतीय मानक (Indian Standard) कैसे खोजें?",
        "बीआईएस उत्पाद प्रमाणन प्रक्रिया क्या है?",
      ],
    },
    chat: {
      inputPlaceholder: "बीआईएस सहायक से कुछ भी पूछें...",
      sendTooltip: "संदेश भेजें",
      disclaimer: "बीआईएस सहायक केवल आधिकारिक भारतीय मानक ब्यूरो अभिलेखों से उत्तर देता है।",
      groundedBadge: "सत्यापित बीआईएस स्रोत",
      guidanceBadge: "सार्वजनिक मार्गदर्शन",
      fallbackHint: "बीआईएस प्रमाणन, हॉलमार्किंग, एचयूआईडी, भारतीय मानक, प्रयोगशाला परीक्षण, या उपभोक्ता शिकायतों के बारे में पूछें।",
      searching: "सहायक बीआईएस ज्ञानकोष की जांच कर रहा है…",
      synthesizing: "सत्यापित उत्तर तैयार किया जा रहा है…",
      sourcesTitle: "स्रोत",
      verifySource: "आधिकारिक बीआईएस स्रोत",
      retry: "पुनः प्रयास करें",
      errorConnect: "आपके अनुरोध को संसाधित करते समय कुछ समस्या आई। कृपया पुनः प्रयास करें।",
      errorDemand: "सेवा पर वर्तमान में अधिक लोड है। कृपया कुछ पलों बाद पुनः प्रयास करें।",
    },
  },
};
