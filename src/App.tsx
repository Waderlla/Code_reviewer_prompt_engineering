import { useState, FormEvent } from "react";

interface ReviewReport {
  overall_score: string;
  found_issues: string[];
  improved_code: string;
}

export default function App() {
  const [language, setLanguage] = useState<string>("Python");
  const [scoreScale, setScoreScale] = useState<string>("1-10");
  const [model, setModel] = useState<string>("qwen2.5-coder:7b");
  const [code, setCode] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [reviewResult, setReviewResult] = useState<ReviewReport | null>(null);

  const handleReviewCode = async (e?: FormEvent) => {
    if (e) {
      e.preventDefault();
    }
    if (!code.trim()) return;

    setIsLoading(true);
    setError(null);
    setReviewResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/review", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          code: code,
          language: language,
          score_scale: scoreScale,
          model: model
        })
      });

      if (!response.ok) {
        throw new Error(`Serwer odpowiedział statusem ${response.status} (${response.statusText})`);
      }

      const data = await response.json();
      
      if (data && typeof data.overall_score !== "undefined") {
        setReviewResult({
          overall_score: String(data.overall_score),
          found_issues: Array.isArray(data.found_issues) ? data.found_issues : [],
          improved_code: typeof data.improved_code === "string" ? data.improved_code : ""
        });
      } else {
        throw new Error("Odpowiedź serwera nie zawiera wymaganych pól (overall_score, found_issues, improved_code).");
      }
    } catch (err: any) {
      console.error("Błąd podczas analizy kodu:", err);
      setError(err.message || "Wystąpił błąd sieci podczas próby połączenia z lokalnym serwerem API.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="page" id="app-root">
      <header className="hero">
        <div>
          <p className="eyebrow">Zadanie kursowe · Prompt Engineering</p>
          <h1>AI Code Reviewer</h1>
          <p className="subtitle">Lokalna aplikacja do code review z promptem parametryzowanym i wynikiem CodeReviewResult.</p>
        </div>
        <div className="badge">100% lokalnie · Ollama</div>
      </header>

      <section className="grid">
        <form className="panel form-panel" onSubmit={handleReviewCode}>
          <div className="controls">
            <label>
              Język projektu
              <select 
                name="language" 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="Python">Python</option>
                <option value="JavaScript">JavaScript</option>
                <option value="TypeScript">TypeScript</option>
                <option value="HTML/CSS">HTML/CSS</option>
                <option value="SQL">SQL</option>
                <option value="Inny">Inny</option>
              </select>
            </label>

            <label>
              Skala oceny
              <select 
                name="score_scale" 
                value={scoreScale} 
                onChange={(e) => setScoreScale(e.target.value)}
              >
                <option value="1-10">1-10</option>
                <option value="procentowa 0-100%">procentowa 0-100%</option>
                <option value="szkolna 1-6">szkolna 1-6</option>
              </select>
            </label>

            <label>
              Model lokalny Ollama
              <input 
                name="model" 
                value={model} 
                onChange={(e) => setModel(e.target.value)} 
                placeholder="qwen2.5-coder:7b" 
              />
            </label>
          </div>

          <label className="code-label">
            Kod do analizy
            <textarea 
              name="code" 
              value={code} 
              onChange={(e) => setCode(e.target.value)} 
              placeholder="Wklej tutaj kod..."
            />
          </label>

          <button type="submit" disabled={isLoading}>
            {isLoading ? "Analizowanie..." : "Oceń kod"}
          </button>
        </form>

        <section className="panel result-panel">
          {error ? (
            <div className="error">
              <h2>Błąd</h2>
              <p>{error}</p>
            </div>
          ) : reviewResult ? (
            <>
              <div className="score-card">
                <span>overall_score</span>
                <strong>{reviewResult.overall_score}</strong>
              </div>
              <h2>found_issues</h2>
              <ul className="issues">
                {reviewResult.found_issues.map((issue, idx) => (
                  <li key={idx}>{issue}</li>
                ))}
              </ul>
              <h2>improved_code</h2>
              <pre>
                <code>{reviewResult.improved_code}</code>
              </pre>
            </>
          ) : (
            <div className="empty">
              <h2>Wynik pojawi się tutaj</h2>
              <p>Aplikacja zwróci strukturę CodeReviewResult: overall_score, found_issues i improved_code.</p>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
