import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { TrendingUp, TrendingDown, ArrowRight, Activity, Newspaper, Building2, Wallet } from 'lucide-react'
import { motion } from 'framer-motion'

const Card = ({ children, className = "" }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`glass-panel p-6 ${className}`}
    >
        {children}
    </motion.div>
)

const ScoreGauge = ({ score }) => {
    const color = score > 60 ? '#00f5d4' : score < 40 ? '#ff006e' : '#facc15';

    return (
        <div className="relative w-40 h-40 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90">
                <circle
                    cx="80"
                    cy="80"
                    r="70"
                    stroke="#23263a"
                    strokeWidth="12"
                    fill="transparent"
                />
                <circle
                    cx="80"
                    cy="80"
                    r="70"
                    stroke={color}
                    strokeWidth="12"
                    fill="transparent"
                    strokeDasharray={440}
                    strokeDashoffset={440 - (440 * score) / 100}
                    className="transition-all duration-1000 ease-out"
                />
            </svg>
            <div className="absolute flex flex-col items-center">
                <span className="text-4xl font-bold">{score}</span>
                <span className="text-xs text-gray-400 uppercase tracking-widest mt-1">Score</span>
            </div>
        </div>
    )
}

export default function Dashboard({ data }) {
    const { symbol, prediction, technical_indicators, sentiment, history, fundamentals, financial_history } = data

    const isBullish = prediction.signal.includes('Buy')
    const trendColor = isBullish ? 'text-[#00f5d4]' : prediction.signal.includes('Sell') ? 'text-[#ff006e]' : 'text-yellow-400'

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">

            {/* Main Score & Signal */}
            <Card className="lg:col-span-2 flex flex-col md:flex-row items-center justify-between gap-8">
                <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                        <h2 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500">{symbol}</h2>
                        <span className={`px-4 py-1.5 rounded-full text-sm font-bold bg-white/5 ${trendColor} border border-white/10`}>
                            {prediction.signal.toUpperCase()}
                        </span>
                    </div>
                    <p className="text-2xl font-light text-gray-400 mb-6">
                        ${technical_indicators.price.toFixed(2)}
                    </p>
                    <p className="text-gray-300 leading-relaxed border-l-4 border-blue-500 pl-4">
                        {prediction.summary}
                    </p>
                </div>
                <ScoreGauge score={prediction.score} />
            </Card>

            {/* Quick Stats */}
            <div className="grid grid-rows-2 gap-6">
                <Card className="flex flex-col justify-center">
                    <div className="flex items-center gap-3 mb-2 text-gray-400">
                        <Activity className="w-5 h-5" />
                        <span>RSI (14)</span>
                    </div>
                    <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-bold">{technical_indicators.rsi?.toFixed(1) || 'N/A'}</span>
                        <span className="text-sm text-gray-500">
                            {technical_indicators.rsi > 70 ? 'Overbought' : technical_indicators.rsi < 30 ? 'Oversold' : 'Neutral'}
                        </span>
                    </div>
                </Card>
                <Card className="flex flex-col justify-center">
                    <div className="flex items-center gap-3 mb-2 text-gray-400">
                        <Newspaper className="w-5 h-5" />
                        <span>Sentiment</span>
                    </div>
                    <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-bold capitalize">{sentiment.overall_sentiment}</span>
                        <span className="text-sm text-gray-500">Based on {sentiment.news_count} articles</span>
                    </div>
                </Card>
            </div>

            {/* Chart */}
            <Card className="lg:col-span-2 h-[400px] flex flex-col">
                <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-blue-500" />
                    Price History (30 Days)
                </h3>
                <div className="h-[300px] w-full bg-white/5 rounded-xl border border-white/10 p-2">
                    <p className="text-xs text-gray-500 mb-2">Debug: {history?.length || 0} data points loaded</p>
                    <ResponsiveContainer width="100%" height="90%">
                        <AreaChart data={history}>
                            <defs>
                                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#161822', borderColor: '#333' }}
                                itemStyle={{ color: '#fff' }}
                            />
                            <XAxis dataKey="Date" hide />
                            <YAxis domain={['auto', 'auto']} hide />
                            <Area
                                type="monotone"
                                dataKey="Close"
                                stroke="#3b82f6"
                                strokeWidth={3}
                                fillOpacity={1}
                                fill="url(#colorPrice)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </Card>

            {/* Fundamentals Section */}
            <Card className="lg:col-span-2 h-[400px] flex flex-col">
                <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-purple-500" />
                    Annual Financial Performance
                </h3>
                <div className="h-[300px] w-full bg-white/5 rounded-xl border border-white/10 p-2">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={financial_history}>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#161822', borderColor: '#333' }}
                                itemStyle={{ color: '#fff' }}
                                formatter={(value) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: "compact" }).format(value)}
                            />
                            <Legend />
                            <XAxis dataKey="date" stroke="#9ca3af" />
                            <YAxis hide />
                            <Bar dataKey="revenue" name="Total Revenue" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="net_income" name="Net Income" fill="#10b981" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </Card>

            {/* Fundamental Details */}
            <Card>
                <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                    <Wallet className="w-5 h-5 text-green-500" />
                    Key Fundamentals
                </h3>
                <div className="space-y-4">
                    <div className="flex justify-between py-3 border-b border-white/5">
                        <span className="text-gray-400">Market Cap</span>
                        <span className="font-mono text-white">
                            {fundamentals?.marketCap ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: "compact" }).format(fundamentals.marketCap) : 'N/A'}
                        </span>
                    </div>
                    <div className="flex justify-between py-3 border-b border-white/5">
                        <span className="text-gray-400">P/E Ratio</span>
                        <span className={`font-mono ${fundamentals?.peRatio > 50 ? 'text-red-400' : 'text-green-400'}`}>
                            {fundamentals?.peRatio?.toFixed(2) || 'N/A'}
                        </span>
                    </div>
                    <div className="flex justify-between py-3 border-b border-white/5">
                        <span className="text-gray-400">EPS (TTM)</span>
                        <span className="font-mono text-white">${fundamentals?.eps?.toFixed(2) || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between py-3 border-b border-white/5">
                        <span className="text-gray-400">Sector</span>
                        <span className="font-mono text-sm text-gray-300 text-right">{fundamentals?.sector || 'N/A'}</span>
                    </div>
                </div>
            </Card>

            {/* Technical Details */}
            <Card>
                <h3 className="text-lg font-semibold mb-6">Technical Data</h3>
                <div className="space-y-4">
                    <div className="flex justify-between py-3 border-b border-white/5">
                        <span className="text-gray-400">SMA (50)</span>
                        <span className="font-mono">${technical_indicators.sma_50?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between py-3 border-b border-white/5">
                        <span className="text-gray-400">MACD</span>
                        <span className={`font-mono ${technical_indicators.macd > 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {technical_indicators.macd?.toFixed(2)}
                        </span>
                    </div>
                    <div className="flex justify-between py-3 border-b border-white/5">
                        <span className="text-gray-400">Bollinger Upper</span>
                        <span className="font-mono">${technical_indicators.bb_upper?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between py-3 border-b border-white/5">
                        <span className="text-gray-400">Bollinger Lower</span>
                        <span className="font-mono">${technical_indicators.bb_lower?.toFixed(2)}</span>
                    </div>
                </div>
            </Card>

            {/* News Feed */}
            <Card className="lg:col-span-3">
                <h3 className="text-lg font-semibold mb-6">Recent News Analysis</h3>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {sentiment.news.slice(0, 3).map((item, i) => (
                        <a key={i} href={item.link} target="_blank" rel="noopener noreferrer"
                            className="block p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors border border-white/5 group">
                            <div className="flex justify-between items-start mb-2">
                                <span className={`text-xs px-2 py-1 rounded-md ${item.sentiment.label === 'Positive' ? 'bg-green-500/20 text-green-400' :
                                    item.sentiment.label === 'Negative' ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-400'
                                    }`}>
                                    {item.sentiment.label}
                                </span>
                                <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-white transition-colors" />
                            </div>
                            <h4 className="font-medium text-sm leading-snug text-gray-200 group-hover:text-blue-400 transition-colors mb-2">
                                {item.title}
                            </h4>
                            <p className="text-xs text-gray-500">{new Date(item.published).toLocaleDateString()}</p>
                        </a>
                    ))}
                    {sentiment.news.length === 0 && (
                        <p className="text-gray-500">No recent news found.</p>
                    )}
                </div>
            </Card>

        </div>
    )
}
