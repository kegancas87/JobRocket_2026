import { Navigate } from "react-router-dom";

const TestPage01 = () => {
  // Admin gate — replace with your real admin check (JWT role, user.role === 'admin', etc.)
  const isAdmin = localStorage.getItem("isAdmin") === "true";

  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }

  return (
    <div
      data-testid="testpage01-container"
      style={{
        fontFamily:
          '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        maxWidth: "760px",
        margin: "40px auto",
        padding: "0 20px",
        lineHeight: 1.6,
        color: "#1f2937",
        background: "#f9fafb",
        minHeight: "100vh",
      }}
    >
      <span
        style={{
          display: "inline-block",
          background: "#6366f1",
          color: "white",
          padding: "4px 10px",
          borderRadius: "999px",
          fontSize: "12px",
          letterSpacing: "0.5px",
        }}
      >
        TEST PAGE 01 &middot; ADMIN ONLY
      </span>
      <h1
        style={{
          color: "#111827",
          borderBottom: "2px solid #6366f1",
          paddingBottom: "8px",
        }}
      >
        Welcome to Test Page 01
      </h1>
      <p>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus lacinia
        odio vitae vestibulum vestibulum. Cras venenatis euismod malesuada.
        Integer in mauris eu nibh euismod gravida.
      </p>

      <h2 style={{ color: "#374151", marginTop: "32px" }}>About this page</h2>
      <p>
        This page is restricted to admin users. It contains random filler
        content used for testing access control and rendering behavior.
      </p>

      <h2 style={{ color: "#374151", marginTop: "32px" }}>Random Facts</h2>
      <ul>
        <li>Octopuses have three hearts and blue blood.</li>
        <li>Honey never spoils.</li>
        <li>Bananas are technically berries, but strawberries are not.</li>
        <li>A group of flamingos is called a "flamboyance".</li>
        <li>The Eiffel Tower can grow more than 6 inches taller in summer.</li>
      </ul>

      <footer
        style={{ marginTop: "48px", fontSize: "12px", color: "#6b7280" }}
      >
        &copy; 2026 Test Page 01 &middot; Admin-only content
      </footer>
    </div>
  );
};

export default TestPage01;
