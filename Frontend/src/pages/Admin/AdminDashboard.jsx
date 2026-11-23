import Sidebar from '../../components/Sidebar.jsx'
import Navbar from '../../pages/Landing/Navbar.jsx'

export default function AdminDashboard() {
  return (
    <div className="flex min-h-screen bg-canvas font-grotesk text-ink">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="flex-1 p-6">
          <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
          <p>Welcome, admin! Here you can manage users, view analytics, and configure the system.</p>
          {/* Add admin widgets or panels here */}
        </main>
      </div>
    </div>
  )
}
