import { SearchMap } from "@/components/hero/SearchMap";
import styles from "@/components/hero/hero.module.css";
import { Plate } from "@/components/sign/Plate";

// data-avoid marks the text that sits over the map on a wide screen, so SearchMap keeps the start and end labels clear of it.
export function MapSection() {
  return (
    <Plate tone="blue" id="map" labelledBy="map-title" className={styles.root}>
      <div className={styles.copy}>
        <h1 id="map-title" className={`display ${styles.title}`}>
          <span className={styles.legend} data-avoid>
            Seoul shortest paths
          </span>{" "}
          <span className={styles.legend} data-avoid>
            The same answer for less
          </span>
        </h1>
      </div>
      <p className={styles.lede} data-avoid>
        Four exact methods on one road network. Every road that turns white is one our Python code settled, in the
        order it settled it.
      </p>
      <SearchMap />
      <p className={`credit ${styles.credit}`}>
        Road data ©{" "}
        <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">
          OpenStreetMap contributors, ODbL
        </a>
      </p>
    </Plate>
  );
}
