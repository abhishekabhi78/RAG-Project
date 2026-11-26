
import { useRef, useState, useEffect } from "react";
import "./App.css";

const API_URL = "https://rag-project-xyld.onrender.com";

function App() {
  const fileInput = useRef(null);

  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [documentSearched, setDocumentSearched] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [asking, setAsking] = useState(false);

  const [chatHistory, setChatHistory] = useState(() => {
  const savedChats = localStorage.getItem("docbox_chat_history");
  return savedChats ? JSON.parse(savedChats) : [];
});
useEffect(() => {
  localStorage.setItem(
    "docbox_chat_history",
    JSON.stringify(chatHistory)
  );
}, [chatHistory]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  useEffect(() => {
  if (messages.length === 0) return;

  const chatId = activeChatId || Date.now();

  if (!activeChatId) {
    setActiveChatId(chatId);
  }

  const title =
    messages.find((m) => m.role === "user")?.content?.slice(0, 35) ||
    uploadResult?.filename ||
    "New conversation";

  const updatedChat = {
    id: chatId,
    title,
    messages: messages,
    document: uploadResult,
  };

  setChatHistory((prev) => {
    const exists = prev.some((chat) => chat.id === chatId);

    if (exists) {
      return prev.map((chat) =>
        chat.id === chatId ? updatedChat : chat
      );
    }

    return [updatedChat, ...prev];
  });
}, [messages, activeChatId, uploadResult]);

  const uploadDocument = async (selectedFile) => {
    if (!selectedFile) return;

    setFile(selectedFile);
    setUploading(true);
    setUploadError("");
    setUploadResult(null);
    setDocumentSearched(false);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(`${API_URL}/api/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      setUploadResult(data);
      setFile(null);


    } catch (error) {
      setUploadError(error.message);
    } finally {
      setUploading(false);

      if (fileInput.current) {
        fileInput.current.value = "";
      }
    }
  };

  const askQuestion = async (customQuestion, isAutomatic = false) => {
    const currentQuestion = (customQuestion || question).trim();
    console.log("Selected PDF:", uploadResult?.filename);

    if (!currentQuestion || asking) return;

    setQuestion("");

    if (!isAutomatic) {
      setMessages((prev) => [
  ...prev,
  {
    role: "user",
    content: currentQuestion,
    attachment: !documentSearched
  ? uploadResult?.filename || null
  : null,
  },
]);
    }

    setAsking(true);

    try {
      const response = await fetch(`${API_URL}/api/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
  query: currentQuestion,
  k: 5,
  filename: uploadResult?.filename,
}),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Request failed");
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        },
      ]);
      setDocumentSearched(true);

    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${error.message}`,
        },
      ]);
    } finally {
      setAsking(false);
    }
  };

  const newChat = () => {
  setMessages([]);
  setActiveChatId(null);
  setQuestion("");
  setUploadError("");
  setUploadResult(null);
  
};

const openChat = (chat) => {
  setMessages(chat.messages);
  setActiveChatId(chat.id);
  setUploadResult(chat.document);
  setQuestion("");
  setUploadError("");
  
};
  return (
    <div className={`docbox-app ${sidebarOpen ? "sidebar-visible" : "sidebar-hidden"}`}>

      {/* LEFT SIDEBAR */}

      <aside className={`docbox-sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>

        <div className="sidebar-top">

  <div className="sidebar-brand">
  <div className="docbox-logo">D</div>
  <span>DocBox AI</span>

  <button
    className="sidebar-toggle"
    onClick={() => setSidebarOpen(!sidebarOpen)}
    title="Toggle sidebar"
  >
    ☰
  </button>
</div>

</div>

        <button className="sidebar-new-chat" onClick={newChat}>
          <span>＋</span>
          New Chat
        </button>

        <button
          className="sidebar-upload"
          onClick={() => fileInput.current?.click()}
          disabled={uploading}
        >
          <span>↥</span>
          Upload Document
        </button>

        <div className="sidebar-history">

          <div className="sidebar-section-title">
            RECENT CHATS
          </div>

          {chatHistory.length === 0 ? (
            <div className="sidebar-empty">
              Your conversations will appear here.
            </div>
          ) : (
            chatHistory.map((chat) => (
              <button
                className="history-item"
                key={chat.id}
                onClick={() => openChat(chat)}
                title={chat.title}
              >
                <span>◷</span>
                <span className="history-title">{chat.title}</span>
              </button>
            ))
          )}

        </div>

        <div className="sidebar-bottom">
          <div className="sidebar-user-icon">D</div>
          <div className="sidebar-user-info">
            <strong>DocBox AI</strong>
          </div>
        </div>

      </aside>
      {!sidebarOpen && (
  <button
    className="sidebar-reopen"
    onClick={() => setSidebarOpen(true)}
    title="Open sidebar"
  >
    ☰
  </button>
)}

      {/* MOBILE OVERLAY */}

      {sidebarOpen && (
        <div
          className="sidebar-overlay"/>
      )}

      {/* MAIN AREA */}

      <div className="docbox-content">

       

        <main className="docbox-main">

          <section className="docbox-chat">

            {messages.length === 0 ? (

              <div className="docbox-welcome">

                <div className="docbox-welcome-icon">✦</div>

                <div className="docbox-eyebrow">
                  YOUR PERSONAL DOCUMENT ASSISTANT
                </div>

                <h1>What would you like to know?</h1>

                <p>
                  Upload your document and let DocBox AI help
                  you understand, explore and find answers.
                </p>

                {!uploadResult && (
                  <button
                    className="welcome-upload"
                    onClick={() => fileInput.current?.click()}
                    disabled={uploading}
                  >
                    <span className="welcome-upload-icon">↥</span>
                    <span>
                      <strong>
                        {uploading
                          ? "Uploading document..."
                          : "Upload a document"}
                      </strong>
                      <small>Choose a PDF or DOCX file</small>
                    </span>
                  </button>
                )}

                <div className="quick-prompts">
                  <button onClick={() => setQuestion("Summarize my document")}>
                    ↗ Summarize my document
                  </button>

                  <button onClick={() => setQuestion("What are the main topics?")}>
                    ↗ What are the main topics?
                  </button>
                </div>

              </div>

            ) : (

              <div className="docbox-messages">

                {messages.map((message, index) => (
                  <div
                    className={`docbox-message ${message.role}`}
                    key={index}
                  >

                  

                    <div className="message-bubble">

                      {message.role === "user" && (
          <div className="message-author">You</div>
        )}
                  {message.attachment && (
  <div className="chat-attachment">
    <span>📄</span>
    <span>{message.attachment}</span>
  </div>
)}
                      <div className="message-text">
                        {message.content}
                      </div>

                    </div>
                  </div>
                ))}
                {asking && (
  <div className="thinking-indicator">
    <span className="thinking-dot"></span>
    <span className="thinking-dot"></span>
    <span className="thinking-dot"></span>
    <span>Thinking...</span>
  </div>
)}

                

              </div>
            )}

            {uploadError && (
              <div className="docbox-error">{uploadError}</div>
            )}

            <div className="docbox-input-area">

              {uploading && (
                <div className="upload-progress">
                  Uploading and processing your document...
                </div>
              )}

              {uploadResult && !documentSearched && (
                <div className="input-document">
                  <span>PDF</span>
                  <strong>{uploadResult.filename}</strong>

                  <button
                    type="button"
                    onClick={() => fileInput.current?.click()}
                  >
                    Replace
                  </button>
                </div>
              )}

              <div className="docbox-composer">

                <input
                  ref={fileInput}
                  type="file"
                  accept=".pdf,.docx"
                  hidden
                  onChange={(e) => {
                    const selectedFile = e.target.files?.[0];
                    if (selectedFile) uploadDocument(selectedFile);
                  }}
                />

                <button
                  className="attach-button"
                  type="button"
                  onClick={() => fileInput.current?.click()}
                  disabled={uploading}
                  title="Upload document"
                >
                  +
                </button>

                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      askQuestion();
                    }
                  }}
                  placeholder="Ask anything about your document..."
                  rows={1}
                />

                <button
                  className="docbox-send"
                  onClick={() => {
  if (question.trim()) {
    askQuestion();
  } else if (uploadResult) {
    askQuestion(
      "Explain this uploaded document in simple language. Give me an overview, its main topics, important points, key findings, and conclusion. Organize the explanation with clear headings.",
      true
    );
  }
}}
                  disabled={(!question.trim() && !uploadResult) || asking}
                  title="Send message"
                >
                  ↑
                </button>

              </div>

              

            </div>

          </section>

        </main>

       

      </div>

    </div>
  );
}

export default App;
