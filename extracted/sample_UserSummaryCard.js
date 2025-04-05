UserSummaryCard = ({ user }) => {
  return (
    <div className="user-summary-card">
      <strong>{user.name}</strong>
      <small>{user.role}</small>
    </div>
  );
}