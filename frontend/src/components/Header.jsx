function Header() {
  return (
    <div className="mb-6 border-b border-green-800 pb-4">
      <h1 className="text-2xl mb-2">
        <span className="text-green-500">~/</span>terminal-music-player
      </h1>
      <p className="text-green-600 text-sm">$ music-player --interactive</p>
    </div>
  );
}

export default Header;