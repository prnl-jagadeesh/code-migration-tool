function Dashboard({ initialUsers, title }) {
  const [users, setUsers] = useState(initialUsers || []);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    if (users.length === 0) {
      setLoading(true);
      fetch('/api/users')
        .then(res => res.json())
        .then(data => {
          setUsers(data);
          setLoading(false);
        })
        .catch(err => {
          console.error('Failed to load users:', err);
          setLoading(false);
        });
    }
  }, []);

  function handleSearch(e) {
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