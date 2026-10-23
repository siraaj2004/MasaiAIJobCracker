import React, { useEffect, useState } from "react";
import { api } from "./api.js";

// Dashboard + quiz + coding + interview + video lesson UI (mobile friendly).
// Quiz answers are never shown before submit: /quiz returns no correct_index.
export default function App() {
  const [dash, setDash] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [code, setCode] = useState("numbers = [10, 20, 30]\nprint(sum(numbers))");
  const [codeOut, setCodeOut] = useState(null);
  useEffect(() => { api("/dashboard").then(setDash); }, []);
  const loadQuiz = async (id) => setQuiz(await api(`/quiz/${id}`));
  const submit = async (id) => setResult(await api(`/quiz/${id}/submit`,
    {method: "POST", body: JSON.stringify({answers})}));
  return (<main>
    <h1>MASAI AI Engineer Job Cracker</h1>
    <p>Telugu AI Mentor — video, quiz, coding, interview, revision okka chota.</p>
    {dash && <section><h2>AI Engineer Readiness: {dash.overall_job_readiness}%</h2>
      {Object.entries(dash.readiness_percent).map(([k, v]) =>
        <div key={k}>{k}: <progress value={v} max="100" /> {v}%</div>)}
      <p>{dash.note}</p></section>}
    <section><h2>Interactive Quiz</h2>
      <input placeholder="Quiz ID" id="qid" />
      <button onClick={() => loadQuiz(document.getElementById("qid").value)}>Load quiz</button>
      {quiz && quiz.questions.map((q, i) => <div key={q.id}>
        <p>{i + 1}/{quiz.questions.length} — {q.question}</p>
        {q.options.map((o, oi) => <label key={oi}>
          <input type="radio" name={"q" + q.id}
            onChange={() => setAnswers({...answers, [q.id]: oi})} /> {o}</label>)}
      </div>)}
      {quiz && <button onClick={() => submit(document.getElementById("qid").value)}>Submit</button>}
      {result && <div><h3>Score: {result.score}% — {result.next_action}</h3>
        {result.detail.filter(d => !d.correct).map(d =>
          <p key={d.id}>Mistake concept: {d.concept}. {d.simple_explanation}</p>)}</div>}
    </section>
    <section><h2>Coding Practice</h2>
      <textarea value={code} onChange={e => setCode(e.target.value)} rows="6" cols="60" />
      <div><button onClick={async () => setCodeOut(await api("/coding/run",
        {method: "POST", body: JSON.stringify({code})}))}>Run</button>
      <button onClick={() => setCode("numbers = [10, 20, 30]\nprint(sum(numbers))")}>Reset</button>
      <button onClick={() => alert("Hint: sum() anni numbers kaluputhundi")}>Hint</button></div>
      {codeOut && <pre>{codeOut.stdout || codeOut.error || codeOut.stderr}</pre>}
    </section>
    <section><h2>Video Lesson + Checkpoint</h2>
      <p>Video play chesthunna madhya lo pause chesi checkpoint interview question ki answer cheyyandi, tarvata continue cheyyandi. Videos open from the storage links in your email / lesson page.</p>
    </section>
  </main>);
}
