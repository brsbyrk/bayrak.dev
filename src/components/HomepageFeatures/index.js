import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Systems & Rust',
    Svg: null,
    description: (
      <>
        Building performant, reliable systems with Rust. From algorithmic trading engines to spatial AI agents and world simulation.
      </>
    ),
  },
  {
    title: 'Projects & Products',
    Svg: null,
    description: (
      <>
        End-to-end product thinking — from concept through implementation. Desktop apps, dev tooling, and experimental workflows.
      </>
    ),
  },
  {
    title: 'Ideas & Experiments',
    Svg: null,
    description: (
      <>
        Exploring new angles on old problems. Procedural music, compression research, and whatever else seems interesting.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
