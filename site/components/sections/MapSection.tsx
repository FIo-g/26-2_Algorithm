import { HERO_SOURCE_LINE } from "@/components/hero/data";
import styles from "@/components/hero/hero.module.css";
import { SearchMap } from "@/components/hero/SearchMap";
import { cardFacts, HERO_GRAPHS, loadHeroFile } from "@/components/hero/summary";
import { MethodGlyph } from "@/components/sign/MethodGlyph";
import { METHOD_COPY } from "@/lib/method-copy";
import { METHODS, type MethodId } from "@/lib/methods";

function copyOf(id: MethodId): string {
  return id === "alt4" || id === "alt8" || id === "alt16" ? METHOD_COPY.alt : METHOD_COPY[id];
}

// SearchMap reads data-intro, data-stage, data-avoid, data-card and data-step: it measures the text and the resting
// cards that sit over the map on a wide screen, and the steps pick the method as the page scrolls.
export function MapSection() {
  const { graphs, order } = loadHeroFile();
  return (
    <section id="map" aria-labelledby="map-title" className={styles.root}>
      <div className={styles.intro} data-intro>
        <h1 id="map-title" className={`display ${styles.title}`}>
          <span className={styles.legend} data-avoid="above">
            Seoul shortest paths
          </span>{" "}
          <span className={styles.legend} data-avoid="above">
            The same answer for less
          </span>
        </h1>
        <p className={styles.lede} data-avoid="above">
          Four exact methods on one road network. Every road that turns white is one our Python code settled, in the
          order it settled it.
        </p>
      </div>
      <div className={styles.stage} data-stage>
        <SearchMap />
        <p className={`credit ${styles.credit}`}>
          Road data ©{" "}
          <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">
            OpenStreetMap contributors, ODbL
          </a>
        </p>
      </div>
      <ol className={styles.steps} role="list">
        {order.map((id) => (
          <li key={id} className={styles.step} data-step={id}>
            <div className={styles.card} data-card>
              <h2 className={styles.cardTitle}>
                <MethodGlyph method={id} />
                {METHODS[id].label}
              </h2>
              <p>{copyOf(id)}</p>
              {HERO_GRAPHS.map((key) => (
                <p key={key} className={styles.facts} data-for={key}>
                  {cardFacts(graphs[key], id)}
                </p>
              ))}
            </div>
          </li>
        ))}
      </ol>
      <p className={`source ${styles.notes}`}>{HERO_SOURCE_LINE}</p>
    </section>
  );
}
