import React, { FunctionComponent } from 'react';

interface User {
  name: string;
  role: string;
}

interface UserSummaryCardProps {
  user: User;
}

const UserSummaryCard: FunctionComponent<UserSummaryCardProps> = ({ user }) => {
  return (
    <div className="user-summary-card">
      <strong>{user.name}</strong>
      <small>{user.role}</small>
    </div>
  );
}

export default UserSummaryCard;