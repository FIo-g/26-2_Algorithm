// The back of the sign: a full-width steel band. Team names are the only Hangul on the page.
export function TeamSection() {
  return (
    <footer id="team" className="site-footer">
      <div className="flow">
        <h2>Team C2, DCCS309 Algorithms</h2>
        <ul className="sign-list">
          <li>
            <span lang="ko">권세현</span> Kwon Sehyun (problem and data)
          </li>
          <li>
            <span lang="ko">김태형</span> Kim Taehyeong (algorithms)
          </li>
          <li>
            <span lang="ko">정의종</span> Jeong Uijong (results and outlook)
          </li>
        </ul>
        <p className="small">
          Road data: OpenStreetMap (© OpenStreetMap contributors, ODbL). Non-commercial coursework.
        </p>
        <p className="small">Results frozen on 2026-11-09 (git tag results-frozen).</p>
        <p className="small">
          Built with generative AI assistance (Claude Code). Usage is logged in docs/ai-usage.md in the repository.
        </p>
      </div>
    </footer>
  );
}
