import { useState } from 'react'
import { Search, TrendingUp, TrendingDown, Activity, DollarSign, PieChart } from 'lucide-react'
import axios from 'axios'
import Dashboard from './components/Dashboard'

function App() {
  const [symbol, setSymbol] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!symbol) return

    setLoading(true)
    setError(null)
    setData(null)

    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/analysis/${symbol.toUpperCase()}`)
      setData(response.data)
    } catch (err) {
      console.error(err)
      setError(`Failed to fetch data: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen pb-20">
      {/* Header */}
      <header className="glass-panel sticky top-0 z-50 border-b border-white/5">
        <div className="container h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Activity className="text-white w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
              StockMind AI
            </h1>
          </div>

          <form onSubmit={handleSearch} className="relative w-96">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search ticker (e.g. AAPL, NVDA)..."
              className="w-full pl-12 bg-[#23263a] py-3 rounded-xl focus:ring-2 ring-blue-500/50"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
            />
          </form>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mt-10">
        {!data && !loading && !error && (
          <div className="flex flex-col items-center justify-center mt-32 text-center animate-float">
            <div className="w-24 h-24 rounded-full bg-blue-500/10 flex items-center justify-center mb-6">
              <PieChart className="w-12 h-12 text-blue-400" />
            </div>
            <h2 className="text-4xl font-bold mb-4">Market Intelligence, Simplified.</h2>
            <p className="text-gray-400 max-w-lg text-lg">
              Enter a stock symbol above to get real-time technical, fundamental, and sentiment analysis powered by AI.
            </p>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center mt-32">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-6 text-xl animate-pulse text-blue-400">Analyzing Market Data...</p>
          </div>
        )}

        {error && (
          <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-2xl mt-10 text-red-200 text-center">
            {error}
          </div>
        )}

        {data && <Dashboard data={data} />}
      </main>
    </div>
  )
}

export default App
