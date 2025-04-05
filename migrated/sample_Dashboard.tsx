import React, { useState, useEffect, ChangeEvent } from 'react';

interface User {
  id: string;
  name: string;
}

interface DashboardProps {
  initialUsers?: User[];
  title: string;
}

const Dashboard: React.FC<DashboardProps> = ({ initialUsers = [], title }) => {
  const [users, setUsers] = useState<User[]>(initialUsers);
  const [loading, setLoading] = useState<boolean>(false);
  const [filter, setFilter] = useState<string>('');

  useEffect(() => {
    if (users.length === 0) {
      setLoading(true);
      fetch('/api/users')
        .then(res => res.json())
        .then((data: User[]) => {
          setUsers(data);
          setLoading(false);
        })
        .catch(err => {
          console.error('Failed to load users:', err);
          setLoading(false);
        });
    }
  }, []);

  const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
    setFilter(e.target.value);
  }

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="dashboard">
      <h1>{title}</h1>
      <input
        type="text"
        placeholder="Search users"
        value={filter}
        onChange={handleSearch}
      />
      {loading ? (
        <Loader />
      ) : (
        <div className="user-grid">
          {filteredUsers.map(user => (
            <UserCard key={user.id} user={user} />
          ))}
        </div>
      )}
    </div>
  );
}

export default Dashboard;