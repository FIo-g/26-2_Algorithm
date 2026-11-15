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

export function MapSection() {
  const { graphs, order } = loadHeroFile();
  // Every method and both graphs are in the HTML; SearchMap shows the selected method, CSS the graph on the map.
  const explain = order.map((id) => ({
    id,
    body: (
      <>
        <p className={styles.name}>
          <MethodGlyph method={id} />
          {METHODS[id].label}
        </p>
        <p>{copyOf(id)}</p>
        {HERO_GRAPHS.map((key) => (
          <p key={key} className={styles.facts} data-for={key}>
            {cardFacts(graphs[key], id)}
          </p>
        ))}
      </>
    ),
  }));
  return (
    <section id="map" aria-labelledby="map-title" className={styles.root}>
      <h1 id="map-title" className={`display ${styles.title}`}>
        <span className={styles.legend}>Seoul shortest paths</span>{" "}
        <span className={styles.legend}>The same answer for less</span>
      </h1>
      <p className={styles.lede}>
        Four exact methods on one road network. Every road that turns white is one our Python code settled, in the
        order it settled it.
      </p>
      <SearchMap explain={explain} />
      <p className={`source ${styles.notes}`}>{HERO_SOURCE_LINE}</p>
      <p className={`credit ${styles.credit}`}>
        Road data ©{" "}
        <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">
          OpenStreetMap contributors, ODbL
        </a>
      </p>
    </section>
  );
}
