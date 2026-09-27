import { profile } from "@/data/profile";
import { DownloadIcon, GitHubIcon, LinkedInIcon, MailIcon } from "./Icons";
import styles from "./Sidebar.module.css";

export default function Sidebar() {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.identity}>
        <div className={styles.nameRow}>
          <div className={styles.avatar} aria-hidden>
            {profile.initials}
          </div>
          <div>
            <div className={styles.nickname}>{profile.nickname}</div>
            <h1 className={styles.name}>{profile.name}</h1>
          </div>
        </div>
        <p className={styles.role}>{profile.role}</p>
        <p className={styles.location}>{profile.location}</p>
        <div className={styles.links}>
          <a className={styles.linkButton} href={profile.links.github} target="_blank" rel="noreferrer">
            <GitHubIcon /> GitHub
          </a>
          <a className={styles.linkButton} href={profile.links.linkedin} target="_blank" rel="noreferrer">
            <LinkedInIcon /> LinkedIn
          </a>
          <a className={styles.linkButton} href={`mailto:${profile.links.email}`}>
            <MailIcon /> Email
          </a>
        </div>
      </div>

      <div className={styles.downloads}>
        {profile.downloads.map((file) =>
          file.available ? (
            <a key={file.label} className={styles.downloadButton} href={file.href} download>
              <DownloadIcon /> {file.label}
            </a>
          ) : (
            <span key={file.label} className={`${styles.downloadButton} ${styles.downloadSoon}`} aria-disabled="true">
              <DownloadIcon /> {file.label}
              <span className={styles.soon}>Soon</span>
            </span>
          ),
        )}
      </div>

      <p className={styles.bio}>{profile.bio}</p>

      <section aria-labelledby="projects-heading">
        <h2 id="projects-heading" className={styles.heading}>
          Projects
        </h2>
        <ul className={styles.projects}>
          {profile.projects.map((project) => (
            <li key={project.name} className={styles.project}>
              <div className={styles.projectTop}>
                <span className={styles.projectName}>{project.name}</span>
                <span className={styles.projectLinks}>
                  {project.live && (
                    <a href={project.live} target="_blank" rel="noreferrer">
                      Live ↗
                    </a>
                  )}
                  <a href={project.code} target="_blank" rel="noreferrer">
                    Code ↗
                  </a>
                </span>
              </div>
              <p className={styles.projectSummary}>{project.summary}</p>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="skills-heading">
        <h2 id="skills-heading" className={styles.heading}>
          Skills
        </h2>
        <ul className={styles.skills}>
          {profile.skills.map((skill) => (
            <li key={skill} className={styles.skill}>
              {skill}
            </li>
          ))}
        </ul>
      </section>

      <p className={styles.languages}>{profile.languages}</p>
    </aside>
  );
}
