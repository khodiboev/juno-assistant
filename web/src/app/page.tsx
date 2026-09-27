import Chat from "@/components/Chat";
import Sidebar from "@/components/Sidebar";
import styles from "./page.module.css";

export default function Home() {
  return (
    <div className={styles.page}>
      <Sidebar />
      <Chat />
    </div>
  );
}
