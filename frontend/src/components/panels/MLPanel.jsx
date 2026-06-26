import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import DataTable from 'react-data-table-component'
import { useDropzone } from 'react-dropzone'
import useAtlasStore from '../../store/useAtlasStore'
import {
  uploadMLFile, analyzeMLData, trainMLModel,
  predictML, listMLModels, deleteMLModel,
  getMLChartData, getMLJobStatus, getMLModelInfo,
  clusterMLData, dimReduceML, trainMLNeural,
  tuneMLHyperparams, kfoldML, featureEngineerML, evaluateML
} from '../../services/api'

// ─── Constants ─────────────────────────────────────────────────
const TABS = [
  { id: 'data',      icon: '📂', label: 'DATA' },
  { id: 'analyze',   icon: '📊', label: 'ANALYZE' },
  { id: 'train',     icon: '🤖', label: 'TRAIN' },
  { id: 'cluster',   icon: '🔘', label: 'CLUSTER' },
  { id: 'dimred',    icon: '📉', label: 'DIMRED' },
  { id: 'neural',    icon: '🧠', label: 'NEURAL' },
  { id: 'hptune',    icon: '⚙️',  label: 'HPTUNE' },
  { id: 'kfold',     icon: '♻️',  label: 'KFOLD' },
  { id: 'feateng',   icon: '🔧', label: 'FEATENG' },
  { id: 'evaluate',  icon: '📋', label: 'EVALUATE' },
  { id: 'predict',   icon: '🔮', label: 'PREDICT' },
  { id: 'models',    icon: '📦', label: 'MODELS' },
  { id: 'visualize', icon: '📈', label: 'VISUALIZE' },
]

const tableStyles = {
  table:      { style: { background: 'transparent', color: '#00ffc8' } },
  headRow:    { style: { background: 'rgba(0,255,200,0.06)', borderBottom: '1px solid rgba(0,255,200,0.15)', minHeight: 36 } },
  headCells:  { style: { color: '#00ffc8', fontSize: 11, fontFamily: 'Orbitron, monospace', letterSpacing: 1, paddingLeft: 10 } },
  rows:       { style: { background: 'transparent', minHeight: 32, borderBottom: '1px solid rgba(0,255,200,0.06)', '&:hover': { background: 'rgba(0,255,200,0.04)' } } },
  cells:      { style: { color: '#c0e8d8', fontSize: 12, fontFamily: 'Share Tech Mono, monospace', paddingLeft: 10 } },
  pagination: { style: { background: 'rgba(0,20,16,0.8)', borderTop: '1px solid rgba(0,255,200,0.1)', color: '#00ffc8', minHeight: 40 } },
  noData:     { style: { color: 'rgba(0,255,200,0.4)', fontFamily: 'Rajdhani', fontSize: 14 } },
}

// ─── Root ───────────────────────────────────────────────────────
export default function MLPanel() {
  const [activeTab, setActiveTab] = useState('data')
  const { setMLModels } = useAtlasStore()

  useEffect(() => {
    listMLModels().then(r => { if (r?.success) setMLModels(r.models) }).catch(() => {})
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, height: '100%' }}>
      {/* Tab bar */}
      <div style={{ display: 'flex', gap: 2, background: 'rgba(0,20,16,0.6)', borderRadius: 8, padding: 3, border: '1px solid rgba(0,255,200,0.1)' }}>
        {TABS.map(tab => (
          <motion.button key={tab.id} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            onClick={() => setActiveTab(tab.id)}
            style={{
              flex: 1, padding: '8px 6px', borderRadius: 6, border: 'none', cursor: 'pointer',
              fontFamily: 'Orbitron, monospace', fontSize: 9, letterSpacing: 1,
              background: activeTab === tab.id ? 'rgba(0,255,200,0.12)' : 'transparent',
              color: activeTab === tab.id ? '#00ffc8' : 'rgba(0,255,200,0.35)',
              transition: 'all 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4
            }}>
            <span style={{ fontSize: 14 }}>{tab.icon}</span>
            {tab.label}
          </motion.button>
        ))}
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        <AnimatePresence mode="wait">
          <motion.div key={activeTab}
            initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }} transition={{ duration: 0.15 }}>
            {activeTab === 'data'      && <DataTab />}
            {activeTab === 'analyze'   && <AnalyzeTab />}
            {activeTab === 'train'     && <TrainTab />}
            {activeTab === 'cluster'   && <ClusterTab />}
            {activeTab === 'dimred'    && <DimRedTab />}
            {activeTab === 'neural'    && <NeuralTab />}
            {activeTab === 'hptune'    && <HPTuneTab />}
            {activeTab === 'kfold'     && <KfoldTab />}
            {activeTab === 'feateng'   && <FeatEngTab />}
            {activeTab === 'evaluate'  && <EvaluateTab />}
            {activeTab === 'predict'   && <PredictTab />}
            {activeTab === 'models'    && <ModelsTab />}
            {activeTab === 'visualize' && <VisualizeTab />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}

// ─── 📂 Data Tab ───────────────────────────────────────────────
function DataTab() {
  const { mlDataset, setMLDataset, setMLAnalysis, setMLTrainingResult, setMLPlotData } = useAtlasStore()
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)
  const [cleanOps, setCleanOps] = useState([])

  const onDrop = useCallback(async (accepted) => {
    const file = accepted[0]
    if (!file) return
    setLoading(true)
    setError(null)

    // Cascade reset — new dataset clears all downstream state
    setMLAnalysis(null)
    setMLTrainingResult(null)
    setMLPlotData(null)

    try {
      const res = await uploadMLFile(file)
      if (res.success) {
        const tableCols = res.columns.map(c => ({
          name: c,
          selector: row => row[c],
          sortable: true,
          wrap: true,
          style: { fontSize: 11, fontFamily: 'Share Tech Mono, monospace' }
        }))
        // rawColumns = plain string array, used everywhere else
        setMLDataset({
          ...res,
          columns: tableCols,
          rawColumns: res.columns,
          preview: res.preview,
          fileName: file.name,
        })
      } else {
        setError(res)
      }
    } catch (e) {
      setError({ message: 'Upload failed', suggestion: 'Check the file format and try again.' })
    }
    setLoading(false)
  }, [setMLDataset, setMLAnalysis, setMLTrainingResult, setMLPlotData])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json'],
    },
    maxFiles: 1,
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {/* Drop zone */}
      <div {...getRootProps()} style={{
        border: `2px dashed ${isDragActive ? '#00ffc8' : 'rgba(0,255,200,0.25)'}`,
        borderRadius: 10, padding: 24, textAlign: 'center', cursor: 'pointer',
        background: isDragActive ? 'rgba(0,255,200,0.06)' : 'rgba(0,20,16,0.5)',
        transition: 'all 0.2s'
      }}>
        <input {...getInputProps()} />
        <div style={{ fontSize: 32, marginBottom: 6 }}>📂</div>
        <div style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'rgba(0,255,200,0.6)', letterSpacing: 1 }}>
          {isDragActive ? 'DROP FILE HERE' : 'DROP CSV / EXCEL / JSON'}
        </div>
        <div style={{ fontSize: 10, color: 'rgba(0,255,200,0.3)', marginTop: 4 }}>or click to browse</div>
      </div>

      {loading && <StatusLine text="Loading dataset..." />}
      {error   && <ErrorBlock err={error} />}

      {mlDataset?.preview && (
        <>
          {/* Stats bar */}
          <div style={{ ...card, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <Label>DATASET</Label>
              <span style={{ fontFamily: 'Share Tech Mono', fontSize: 11, color: '#00ffc8' }}>{mlDataset.fileName}</span>
            </div>
            <div style={{ display: 'flex', gap: 16 }}>
              <Stat label="ROWS"    value={mlDataset.shape?.[0]?.toLocaleString()} />
              <Stat label="COLS"    value={mlDataset.shape?.[1]} />
              <Stat label="PREVIEW" value={`${mlDataset.preview.length} rows`} color="rgba(0,255,200,0.4)" />
            </div>
          </div>

          {/* Data table */}
          <div style={card}>
            <DataTable
              columns={mlDataset.columns}
              data={mlDataset.preview.slice(0, 50)}
              customStyles={tableStyles}
              pagination paginationPerPage={10}
              paginationRowsPerPageOptions={[5, 10, 20, 50]}
              highlightOnHover dense
            />
          </div>

          {/* Column types */}
          {mlDataset.dtypes && (
            <div style={card}>
              <Label>COLUMN TYPES</Label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
                {Object.entries(mlDataset.dtypes).map(([col, dt]) => {
                  const isFloat = dt.includes('float')
                  const isInt   = dt.includes('int')
                  const color   = isFloat ? '#00aaff' : isInt ? '#00ffc8' : '#ff88ff'
                  const bg      = isFloat ? 'rgba(0,170,255,0.08)' : isInt ? 'rgba(0,255,200,0.08)' : 'rgba(255,136,255,0.08)'
                  return (
                    <span key={col} style={{ padding: '3px 8px', borderRadius: 4, fontSize: 10, fontFamily: 'Share Tech Mono', background: bg, border: `1px solid ${color}44`, color }}>
                      {col}: {dt}
                    </span>
                  )
                })}
              </div>
            </div>
          )}

          {/* Missing values */}
          {mlDataset.missing && Object.values(mlDataset.missing).some(v => v > 0) && (
            <div style={card}>
              <Label>MISSING VALUES</Label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
                {Object.entries(mlDataset.missing).filter(([, v]) => v > 0).map(([col, count]) => (
                  <span key={col} style={{ padding: '3px 8px', borderRadius: 4, fontSize: 10, fontFamily: 'Share Tech Mono', background: 'rgba(255,85,51,0.08)', border: '1px solid rgba(255,85,51,0.3)', color: '#ff5533' }}>
                    {col}: {count} missing
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

// ─── 📊 Analyze Tab ────────────────────────────────────────────
function AnalyzeTab() {
  const { mlDataset, mlAnalysis, setMLAnalysis } = useAtlasStore()
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const run = async () => {
    if (!mlDataset?.session_id) return
    setLoading(true)
    setError(null)
    try {
      const res = await analyzeMLData({ session_id: mlDataset.session_id })
      if (res.success) setMLAnalysis(res.analysis)
      else setError(res)
    } catch { setError({ message: 'Analysis failed', suggestion: 'Make sure a dataset is loaded.' }) }
    setLoading(false)
  }

  const statsCols = [
    { name: 'STAT', selector: r => r.stat, style: { color: '#00ffc8', fontFamily: 'Share Tech Mono', fontSize: 11 } },
    ...(mlAnalysis?.basic_stats
      ? Object.keys(mlAnalysis.basic_stats).slice(0, 6).map(col => ({
          name: col.toUpperCase(),
          selector: r => typeof r[col] === 'number' ? r[col].toFixed(3) : r[col] ?? '—',
          sortable: true,
          style: { fontFamily: 'Share Tech Mono', fontSize: 11 }
        }))
      : [])
  ]

  const statsData = mlAnalysis?.basic_stats
    ? Object.entries(mlAnalysis.basic_stats).map(([stat, vals]) => ({ stat, ...vals }))
    : []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <Btn onClick={run} disabled={loading || !mlDataset}>
          {loading ? '◌ ANALYZING...' : '📊 ANALYZE DATASET'}
        </Btn>
        {!mlDataset && <Hint>Upload a dataset first</Hint>}
      </div>
      {error && <ErrorBlock err={error} />}

      {mlAnalysis?.basic_stats && (
        <div style={card}>
          <Label>DESCRIPTIVE STATISTICS</Label>
          <div style={{ marginTop: 8 }}>
            <DataTable columns={statsCols} data={statsData} customStyles={tableStyles} dense pagination={false} />
          </div>
        </div>
      )}

      {mlAnalysis?.outliers && Object.keys(mlAnalysis.outliers).length > 0 && (
        <div style={card}>
          <Label>OUTLIERS  (IQR method)</Label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
            {Object.entries(mlAnalysis.outliers).map(([col, info]) => (
              <span key={col} style={{ padding: '4px 10px', borderRadius: 4, fontSize: 11, fontFamily: 'Share Tech Mono', background: 'rgba(255,170,0,0.08)', border: '1px solid rgba(255,170,0,0.3)', color: '#ffaa00' }}>
                {col}: {info.count ?? info} outlier{(info.count ?? info) > 1 ? 's' : ''}
              </span>
            ))}
          </div>
        </div>
      )}

      {mlAnalysis?.skewness && Object.keys(mlAnalysis.skewness).length > 0 && (
        <div style={card}>
          <Label>SKEWNESS</Label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
            {Object.entries(mlAnalysis.skewness).map(([col, val]) => {
              const high = Math.abs(val) > 1
              return (
                <span key={col} style={{ padding: '3px 10px', borderRadius: 4, fontSize: 11, fontFamily: 'Share Tech Mono', background: high ? 'rgba(255,85,51,0.08)' : 'rgba(0,255,200,0.08)', border: `1px solid ${high ? 'rgba(255,85,51,0.3)' : 'rgba(0,255,200,0.2)'}`, color: high ? '#ff5533' : '#00ffc8' }}>
                  {col}: {Number(val).toFixed(3)}
                </span>
              )
            })}
          </div>
        </div>
      )}

      {mlAnalysis?.value_counts && (
        <div style={card}>
          <Label>CATEGORICAL DISTRIBUTIONS</Label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 8 }}>
            {Object.entries(mlAnalysis.value_counts).map(([col, counts]) => (
              <div key={col}>
                <div style={{ fontSize: 10, color: '#ff88ff', fontFamily: 'Share Tech Mono', marginBottom: 4 }}>{col}</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                  {Object.entries(counts).slice(0, 12).map(([k, v]) => (
                    <span key={k} style={{ padding: '2px 8px', borderRadius: 3, fontSize: 10, fontFamily: 'Share Tech Mono', background: 'rgba(255,136,255,0.08)', border: '1px solid rgba(255,136,255,0.2)', color: '#ff88ff' }}>
                      {k}: {v}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!mlAnalysis && mlDataset && !loading && (
        <Hint center>Click ANALYZE DATASET to see statistics</Hint>
      )}
    </div>
  )
}

// ─── 🤖 Train Tab ──────────────────────────────────────────────
function TrainTab() {
  const { mlDataset, mlTrainingResult, setMLTrainingResult, setMLModels } = useAtlasStore()
  const [task, setTask]           = useState('classification')
  const [target, setTarget]       = useState('')
  const [algorithm, setAlgorithm] = useState('auto')
  const [jobId, setJobId]         = useState(null)
  const [jobInfo, setJobInfo]     = useState(null)  // { status, progress, step }
  const [error, setError]         = useState(null)
  const pollRef                   = useRef(null)

  // Poll job status
  useEffect(() => {
    if (!jobId) return
    pollRef.current = setInterval(async () => {
      try {
        const s = await getMLJobStatus(jobId)
        if (!s?.success) return
        setJobInfo(s)
        if (s.status === 'done') {
          clearInterval(pollRef.current)
          setJobId(null)
          const result = s.result
          if (result?.success) {
            setMLTrainingResult(result)
            listMLModels().then(r => { if (r?.success) setMLModels(r.models) })
          } else {
            setError(result)
          }
        } else if (s.status === 'error') {
          clearInterval(pollRef.current)
          setJobId(null)
          setError(s.result)
        }
      } catch {}
    }, 800)
    return () => clearInterval(pollRef.current)
  }, [jobId])

  const runTrain = async () => {
    if (!mlDataset?.session_id || !target) return
    setError(null)
    setMLTrainingResult(null)
    setJobInfo(null)
    try {
      const res = await trainMLModel({
        task,
        session_id: mlDataset.session_id,
        target,
        algorithm,
      })
      if (res.job_id) {
        setJobId(res.job_id)
      } else {
        setError(res)
      }
    } catch {
      setError({ message: 'Could not start training', suggestion: 'Check the backend is running.' })
    }
  }

  const allCols    = mlDataset?.rawColumns || []
  const isTraining = !!jobId

  const algoOptions = {
    classification: [
      { value: 'random_forest',   label: '🌲 Random Forest' },
      { value: 'logistic',        label: '📈 Logistic Regression' },
      { value: 'gradient_boost',  label: '🚀 Gradient Boost' },
      { value: 'svm',             label: '🔲 SVM' },
      { value: 'naive_bayes',     label: '📊 Naive Bayes' },
    ],
    regression: [
      { value: 'random_forest',   label: '🌲 Random Forest' },
      { value: 'linear',          label: '📈 Linear Regression' },
      { value: 'ridge',           label: '⛰️ Ridge' },
      { value: 'gradient_boost',  label: '🚀 Gradient Boost' },
      { value: 'svr',             label: '🔲 SVR' },
    ],
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {!mlDataset && <Hint center>Upload a dataset first</Hint>}

      {mlDataset && (
        <>
          {/* Task */}
          <div style={card}>
            <Label>TASK TYPE</Label>
            <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
              {[
                { id: 'classification', label: 'Classification', icon: '🏷️' },
                { id: 'regression',     label: 'Regression',     icon: '📉' },
                { id: 'auto',           label: 'AutoML',         icon: '⚡' },
              ].map(t => (
                <motion.button key={t.id} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                  onClick={() => { setTask(t.id); setAlgorithm('auto') }}
                  style={{
                    flex: 1, padding: '10px 12px', borderRadius: 8, cursor: 'pointer',
                    border: `1px solid ${task === t.id ? 'rgba(0,255,200,0.5)' : 'rgba(0,255,200,0.12)'}`,
                    background: task === t.id ? 'rgba(0,255,200,0.1)' : 'rgba(0,20,16,0.5)',
                    color: task === t.id ? '#00ffc8' : 'rgba(0,255,200,0.4)',
                    fontFamily: 'Rajdhani', fontSize: 13, transition: 'all 0.2s'
                  }}>
                  {t.icon} {t.label}
                </motion.button>
              ))}
            </div>
          </div>

          {/* Target + Algorithm */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={card}>
              <Label>TARGET COLUMN</Label>
              <select value={target} onChange={e => setTarget(e.target.value)} style={{ ...select, marginTop: 8 }}>
                <option value="">— Select target —</option>
                {allCols.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div style={card}>
              <Label>ALGORITHM</Label>
              <select value={algorithm} onChange={e => setAlgorithm(e.target.value)} style={{ ...select, marginTop: 8 }} disabled={task === 'auto'}>
                <option value="auto">🤖 Auto (Best)</option>
                {(algoOptions[task] || []).map(a => (
                  <option key={a.value} value={a.value}>{a.label}</option>
                ))}
              </select>
            </div>
          </div>

          <Btn onClick={runTrain} disabled={isTraining || !target}>
            {isTraining ? '◌ TRAINING...' : '🤖 TRAIN MODEL'}
          </Btn>

          {error && <ErrorBlock err={error} />}

          {/* Progress bar */}
          {isTraining && jobInfo && (
            <div style={card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontFamily: 'Orbitron', fontSize: 9, color: '#aa66ff', letterSpacing: 1 }}>
                  {jobInfo.step || 'TRAINING...'}
                </span>
                <span style={{ fontFamily: 'Share Tech Mono', fontSize: 10, color: '#aa66ff' }}>
                  {jobInfo.progress || 0}%
                </span>
              </div>
              <div style={{ height: 6, background: 'rgba(153,51,255,0.15)', borderRadius: 3, overflow: 'hidden' }}>
                <motion.div
                  animate={{ width: `${jobInfo.progress || 0}%` }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                  style={{ height: '100%', background: 'linear-gradient(90deg, #9933ff, #ff66ff)', borderRadius: 3 }} />
              </div>
            </div>
          )}

          {/* Result */}
          {mlTrainingResult?.success && (
            <div style={{ ...card, borderColor: 'rgba(0,255,200,0.35)' }}>
              <Label style={{ color: '#00ffc8' }}>✓ TRAINING COMPLETE</Label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 10, marginTop: 10 }}>
                {mlTrainingResult.algorithm && <MetricCard label="ALGORITHM"  value={mlTrainingResult.algorithm.replace(/_/g, ' ').toUpperCase()} color="#ff88ff" small />}
                {mlTrainingResult.accuracy  != null && <MetricCard label="ACCURACY"  value={(mlTrainingResult.accuracy * 100).toFixed(1) + '%'} color="#00ffc8" />}
                {mlTrainingResult.rmse      != null && <MetricCard label="RMSE"       value={mlTrainingResult.rmse} color="#00aaff" />}
                {mlTrainingResult.r2        != null && <MetricCard label="R²"          value={mlTrainingResult.r2?.toFixed(4)} color="#00aaff" />}
                {mlTrainingResult.features  && <MetricCard label="FEATURES"  value={`${mlTrainingResult.features.length} cols`} color="#ffaa00" small />}
              </div>
              {mlTrainingResult.model_id && (
                <div style={{ marginTop: 10, fontSize: 10, color: 'rgba(0,255,200,0.4)', fontFamily: 'Share Tech Mono' }}>
                  ID: {mlTrainingResult.model_id}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

// ─── 🔘 Cluster Tab ────────────────────────────────────────────
function ClusterTab() {
  const { mlDataset, mlClusterResult, setMLClusterResult } = useAtlasStore()
  const [algorithm, setAlgorithm] = useState('kmeans')
  const [nClusters, setNClusters] = useState(3)
  const [eps, setEps] = useState(0.5)
  const [minSamples, setMinSamples] = useState(5)
  const [jobId, setJobId] = useState(null)
  const [jobInfo, setJobInfo] = useState(null)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)

  useEffect(() => {
    if (!jobId) return
    pollRef.current = setInterval(async () => {
      try {
        const s = await getMLJobStatus(jobId)
        if (!s?.success) return
        setJobInfo(s)
        if (s.status === 'done') {
          clearInterval(pollRef.current); setJobId(null)
          s.result?.success ? setMLClusterResult(s.result) : setError(s.result)
        } else if (s.status === 'error') {
          clearInterval(pollRef.current); setJobId(null); setError(s.result)
        }
      } catch {}
    }, 800)
    return () => clearInterval(pollRef.current)
  }, [jobId])

  const run = async () => {
    if (!mlDataset?.session_id) return
    setError(null); setMLClusterResult(null); setJobInfo(null)
    try {
      const res = await clusterMLData({ session_id: mlDataset.session_id, algorithm, n_clusters: nClusters, eps, min_samples: minSamples })
      res.job_id ? setJobId(res.job_id) : setError(res)
    } catch { setError({ message: 'Clustering failed' }) }
  }

  const isRunning = !!jobId
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {!mlDataset && <Hint center>Upload a dataset first</Hint>}
      {mlDataset && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={card}>
              <Label>ALGORITHM</Label>
              <select value={algorithm} onChange={e => setAlgorithm(e.target.value)} style={{ ...select, marginTop: 8 }}>
                <option value="kmeans">K-Means</option>
                <option value="dbscan">DBSCAN</option>
                <option value="mean_shift">Mean Shift</option>
                <option value="agglomerative">Agglomerative</option>
              </select>
            </div>
            <div style={card}>
              <Label>N CLUSTERS</Label>
              <input type="number" value={nClusters} onChange={e => setNClusters(Number(e.target.value))} min={2} max={50} style={{ ...inputSt, marginTop: 8 }} />
            </div>
          </div>
          {algorithm === 'dbscan' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <div style={card}><Label>EPS</Label><input type="number" value={eps} onChange={e => setEps(Number(e.target.value))} step={0.1} style={{ ...inputSt, marginTop: 8 }} /></div>
              <div style={card}><Label>MIN SAMPLES</Label><input type="number" value={minSamples} onChange={e => setMinSamples(Number(e.target.value))} min={1} style={{ ...inputSt, marginTop: 8 }} /></div>
            </div>
          )}
          <Btn onClick={run} disabled={isRunning}>{isRunning ? '◌ CLUSTERING...' : '🔘 RUN CLUSTERING'}</Btn>
          {error && <ErrorBlock err={error} />}
          {isRunning && jobInfo && (
            <div style={card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontFamily: 'Orbitron', fontSize: 9, color: '#aa66ff' }}>{jobInfo.step || 'CLUSTERING...'}</span>
                <span style={{ fontFamily: 'Share Tech Mono', fontSize: 10, color: '#aa66ff' }}>{jobInfo.progress || 0}%</span>
              </div>
              <div style={{ height: 6, background: 'rgba(153,51,255,0.15)', borderRadius: 3, overflow: 'hidden' }}>
                <motion.div animate={{ width: `${jobInfo.progress || 0}%` }} transition={{ duration: 0.4 }} style={{ height: '100%', background: 'linear-gradient(90deg, #9933ff, #ff66ff)', borderRadius: 3 }} />
              </div>
            </div>
          )}
          {mlClusterResult?.success && (
            <div style={{ ...card, borderColor: 'rgba(0,255,200,0.35)' }}>
              <Label style={{ color: '#00ffc8' }}>✓ CLUSTERING COMPLETE</Label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 10 }}>
                <MetricCard label="ALGORITHM" value={mlClusterResult.algorithm?.toUpperCase()} color="#ff88ff" small />
                <MetricCard label="CLUSTERS" value={mlClusterResult.n_clusters} color="#00ffc8" />
                {mlClusterResult.inertia != null && <MetricCard label="INERTIA" value={mlClusterResult.inertia.toFixed(2)} color="#00aaff" small />}
                {mlClusterResult.noise != null && <MetricCard label="NOISE" value={mlClusterResult.noise} color="#ff5533" small />}
              </div>
              {mlClusterResult.labels && (
                <div style={{ marginTop: 12 }}>
                  <Label>LABELS</Label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 6 }}>
                    {mlClusterResult.labels.map((l, i) => (
                      <span key={i} style={{ padding: '2px 8px', borderRadius: 3, fontSize: 10, fontFamily: 'Share Tech Mono', background: 'rgba(0,255,200,0.06)', border: '1px solid rgba(0,255,200,0.15)', color: '#00ffc8' }}>
                        [{i}]{' '}{l}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {mlClusterResult.cluster_centers && (
                <div style={{ marginTop: 12 }}>
                  <Label>CENTERS</Label>
                  {mlClusterResult.cluster_centers.map((c, i) => (
                    <div key={i} style={{ fontSize: 10, color: 'rgba(0,255,200,0.6)', fontFamily: 'Share Tech Mono', marginTop: 4 }}>
                      Cluster {c.cluster} ({c.size} pts): [{c.center.map(v => v.toFixed(3)).join(', ')}]
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

// ─── 📉 DimRed Tab ──────────────────────────────────────────────
function DimRedTab() {
  const { mlDataset, mlDimRedResult, setMLDimRedResult } = useAtlasStore()
  const [algorithm, setAlgorithm] = useState('pca')
  const [nComponents, setNComponents] = useState(2)
  const [jobId, setJobId] = useState(null)
  const [jobInfo, setJobInfo] = useState(null)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)

  useEffect(() => {
    if (!jobId) return
    pollRef.current = setInterval(async () => {
      try {
        const s = await getMLJobStatus(jobId)
        if (!s?.success) return
        setJobInfo(s)
        if (s.status === 'done') {
          clearInterval(pollRef.current); setJobId(null)
          s.result?.success ? setMLDimRedResult(s.result) : setError(s.result)
        } else if (s.status === 'error') {
          clearInterval(pollRef.current); setJobId(null); setError(s.result)
        }
      } catch {}
    }, 800)
    return () => clearInterval(pollRef.current)
  }, [jobId])

  const run = async () => {
    if (!mlDataset?.session_id) return
    setError(null); setMLDimRedResult(null); setJobInfo(null)
    try {
      const res = await dimReduceML({ session_id: mlDataset.session_id, algorithm, n_components: nComponents })
      res.job_id ? setJobId(res.job_id) : setError(res)
    } catch { setError({ message: 'Dim reduction failed' }) }
  }

  const isRunning = !!jobId
  const pts = mlDimRedResult?.components || []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {!mlDataset && <Hint center>Upload a dataset first</Hint>}
      {mlDataset && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={card}>
              <Label>ALGORITHM</Label>
              <select value={algorithm} onChange={e => setAlgorithm(e.target.value)} style={{ ...select, marginTop: 8 }}>
                <option value="pca">PCA</option>
                <option value="tsne">t-SNE</option>
              </select>
            </div>
            <div style={card}>
              <Label>N COMPONENTS</Label>
              <input type="number" value={nComponents} onChange={e => setNComponents(Number(e.target.value))} min={2} max={10} style={{ ...inputSt, marginTop: 8 }} />
            </div>
          </div>
          <Btn onClick={run} disabled={isRunning}>{isRunning ? '◌ REDUCING...' : '📉 RUN DIM REDUCTION'}</Btn>
          {error && <ErrorBlock err={error} />}
          {isRunning && jobInfo && (
            <div style={card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontFamily: 'Orbitron', fontSize: 9, color: '#aa66ff' }}>{jobInfo.step || 'REDUCING...'}</span>
                <span style={{ fontFamily: 'Share Tech Mono', fontSize: 10, color: '#aa66ff' }}>{jobInfo.progress || 0}%</span>
              </div>
              <div style={{ height: 6, background: 'rgba(153,51,255,0.15)', borderRadius: 3, overflow: 'hidden' }}>
                <motion.div animate={{ width: `${jobInfo.progress || 0}%` }} transition={{ duration: 0.4 }} style={{ height: '100%', background: 'linear-gradient(90deg, #9933ff, #ff66ff)', borderRadius: 3 }} />
              </div>
            </div>
          )}
          {mlDimRedResult?.success && (
            <>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
                <MetricCard label="ALGORITHM" value={mlDimRedResult.algorithm?.toUpperCase()} color="#ff88ff" small />
                <MetricCard label="COMPONENTS" value={mlDimRedResult.n_components} color="#00ffc8" />
                {mlDimRedResult.explained_variance_ratio && (
                  <MetricCard label="VAR RATIO" value={mlDimRedResult.explained_variance_ratio.map(v => (v * 100).toFixed(1) + '%').join(', ')} color="#00aaff" small />
                )}
                {mlDimRedResult.cumulative_variance != null && (
                  <MetricCard label="CUM VAR" value={(mlDimRedResult.cumulative_variance * 100).toFixed(1) + '%'} color="#00ffc8" />
                )}
              </div>
              {/* Scatter plot of first 2 components */}
              {pts.length > 0 && nComponents >= 2 && (
                <div style={card}>
                  <Label>PC1 vs PC2 — SCATTER</Label>
                  <DimRedScatter points={pts} />
                </div>
              )}
              {mlDimRedResult.features && (
                <div style={card}>
                  <Label>OUTPUT FEATURES</Label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
                    {mlDimRedResult.features.map(f => (
                      <span key={f} style={{ padding: '3px 8px', borderRadius: 4, fontSize: 10, fontFamily: 'Share Tech Mono', background: 'rgba(0,255,200,0.06)', border: '1px solid rgba(0,255,200,0.15)', color: '#00ffc8' }}>{f}</span>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  )
}

function DimRedScatter({ points }) {
  if (!points || points.length === 0) return null
  const xs = points.map(p => p[0])
  const ys = points.map(p => p[1])
  const xMin = Math.min(...xs), xMax = Math.max(...xs)
  const yMin = Math.min(...ys), yMax = Math.max(...ys)
  const W = 300, H = 180
  const px = v => ((v - xMin) / (xMax - xMin || 1)) * W
  const py = v => H - ((v - yMin) / (yMax - yMin || 1)) * H

  return (
    <svg width={W} height={H} style={{ marginTop: 10, overflow: 'visible' }}>
      {points.map((p, i) => (
        <circle key={i} cx={px(p[0])} cy={py(p[1])} r={2.5}
          fill="rgba(0,255,200,0.45)" stroke="none" />
      ))}
    </svg>
  )
}

// ─── 🧠 Neural Tab ──────────────────────────────────────────────
function NeuralTab() {
  const { mlDataset, mlNeuralResult, setMLNeuralResult } = useAtlasStore()
  const [target, setTarget] = useState('')
  const [taskType, setTaskType] = useState('classification')
  const [hiddenLayers, setHiddenLayers] = useState('100,50')
  const [maxIter, setMaxIter] = useState(500)
  const [jobId, setJobId] = useState(null)
  const [jobInfo, setJobInfo] = useState(null)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)

  useEffect(() => {
    if (!jobId) return
    pollRef.current = setInterval(async () => {
      try {
        const s = await getMLJobStatus(jobId)
        if (!s?.success) return
        setJobInfo(s)
        if (s.status === 'done') {
          clearInterval(pollRef.current); setJobId(null)
          s.result?.success ? setMLNeuralResult(s.result) : setError(s.result)
        } else if (s.status === 'error') {
          clearInterval(pollRef.current); setJobId(null); setError(s.result)
        }
      } catch {}
    }, 800)
    return () => clearInterval(pollRef.current)
  }, [jobId])

  const run = async () => {
    if (!mlDataset?.session_id || !target) return
    setError(null); setMLNeuralResult(null); setJobInfo(null)
    try {
      const res = await trainMLNeural({ session_id: mlDataset.session_id, target, task_type: taskType, hidden_layers: hiddenLayers, max_iter: maxIter })
      res.job_id ? setJobId(res.job_id) : setError(res)
    } catch { setError({ message: 'Neural training failed' }) }
  }

  const allCols = mlDataset?.rawColumns || []
  const isRunning = !!jobId

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {!mlDataset && <Hint center>Upload a dataset first</Hint>}
      {mlDataset && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={card}>
              <Label>TARGET COLUMN</Label>
              <select value={target} onChange={e => setTarget(e.target.value)} style={{ ...select, marginTop: 8 }}>
                <option value="">— Select target —</option>
                {allCols.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div style={card}>
              <Label>TASK TYPE</Label>
              <select value={taskType} onChange={e => setTaskType(e.target.value)} style={{ ...select, marginTop: 8 }}>
                <option value="classification">Classification</option>
                <option value="regression">Regression</option>
              </select>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={card}>
              <Label>HIDDEN LAYERS</Label>
              <input value={hiddenLayers} onChange={e => setHiddenLayers(e.target.value)} placeholder="100,50" style={{ ...inputSt, marginTop: 8 }} />
              <div style={{ fontSize: 8, color: 'rgba(0,255,200,0.3)', fontFamily: 'Share Tech Mono', marginTop: 4 }}>comma-separated neuron counts</div>
            </div>
            <div style={card}>
              <Label>MAX ITERATIONS</Label>
              <input type="number" value={maxIter} onChange={e => setMaxIter(Number(e.target.value))} min={100} max={5000} step={100} style={{ ...inputSt, marginTop: 8 }} />
            </div>
          </div>
          <Btn onClick={run} disabled={isRunning || !target}>{isRunning ? '◌ TRAINING MLP...' : '🧠 TRAIN NEURAL NETWORK'}</Btn>
          {error && <ErrorBlock err={error} />}
          {isRunning && jobInfo && (
            <div style={card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontFamily: 'Orbitron', fontSize: 9, color: '#aa66ff' }}>{jobInfo.step || 'TRAINING MLP...'}</span>
                <span style={{ fontFamily: 'Share Tech Mono', fontSize: 10, color: '#aa66ff' }}>{jobInfo.progress || 0}%</span>
              </div>
              <div style={{ height: 6, background: 'rgba(153,51,255,0.15)', borderRadius: 3, overflow: 'hidden' }}>
                <motion.div animate={{ width: `${jobInfo.progress || 0}%` }} transition={{ duration: 0.4 }} style={{ height: '100%', background: 'linear-gradient(90deg, #9933ff, #ff66ff)', borderRadius: 3 }} />
              </div>
            </div>
          )}
          {mlNeuralResult?.success && (
            <div style={{ ...card, borderColor: 'rgba(0,255,200,0.35)' }}>
              <Label style={{ color: '#00ffc8' }}>✓ MLP TRAINING COMPLETE</Label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 10 }}>
                {mlNeuralResult.accuracy != null && <MetricCard label="ACCURACY" value={(mlNeuralResult.accuracy * 100).toFixed(1) + '%'} color="#00ffc8" />}
                {mlNeuralResult.rmse != null && <MetricCard label="RMSE" value={mlNeuralResult.rmse} color="#00aaff" />}
                {mlNeuralResult.loss != null && <MetricCard label="LOSS" value={mlNeuralResult.loss} color="#ff88ff" small />}
                {mlNeuralResult.layers && <MetricCard label="LAYERS" value={mlNeuralResult.layers} color="#ffaa00" small />}
              </div>
              {mlNeuralResult.model_id && (
                <div style={{ marginTop: 10, fontSize: 10, color: 'rgba(0,255,200,0.4)', fontFamily: 'Share Tech Mono' }}>
                  ID: {mlNeuralResult.model_id}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

// ─── ⚙️ HPTune Tab ──────────────────────────────────────────────
function HPTuneTab() {
  const { mlDataset, mlTuneResult, setMLTuneResult } = useAtlasStore()
  const [target, setTarget] = useState('')
  const [taskType, setTaskType] = useState('classification')
  const [algorithm, setAlgorithm] = useState('random_forest')
  const [cv, setCv] = useState(5)
  const [scoring, setScoring] = useState('accuracy')
  const [jobId, setJobId] = useState(null)
  const [jobInfo, setJobInfo] = useState(null)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)

  useEffect(() => {
    if (!jobId) return
    pollRef.current = setInterval(async () => {
      try {
        const s = await getMLJobStatus(jobId)
        if (!s?.success) return
        setJobInfo(s)
        if (s.status === 'done') {
          clearInterval(pollRef.current); setJobId(null)
          s.result?.success ? setMLTuneResult(s.result) : setError(s.result)
        } else if (s.status === 'error') {
          clearInterval(pollRef.current); setJobId(null); setError(s.result)
        }
      } catch {}
    }, 800)
    return () => clearInterval(pollRef.current)
  }, [jobId])

  const run = async () => {
    if (!mlDataset?.session_id || !target) return
    setError(null); setMLTuneResult(null); setJobInfo(null)
    try {
      const res = await tuneMLHyperparams({ session_id: mlDataset.session_id, target, task_type: taskType, algorithm, cv, scoring })
      res.job_id ? setJobId(res.job_id) : setError(res)
    } catch { setError({ message: 'Hyperparameter tuning failed' }) }
  }

  const allCols = mlDataset?.rawColumns || []
  const isRunning = !!jobId

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {!mlDataset && <Hint center>Upload a dataset first</Hint>}
      {mlDataset && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={card}>
              <Label>TARGET COLUMN</Label>
              <select value={target} onChange={e => setTarget(e.target.value)} style={{ ...select, marginTop: 8 }}>
                <option value="">— Select target —</option>
                {allCols.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div style={card}>
              <Label>TASK TYPE</Label>
              <select value={taskType} onChange={e => setTaskType(e.target.value)} style={{ ...select, marginTop: 8 }}>
                <option value="classification">Classification</option>
                <option value="regression">Regression</option>
              </select>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={card}>
              <Label>ALGORITHM</Label>
              <select value={algorithm} onChange={e => setAlgorithm(e.target.value)} style={{ ...select, marginTop: 8 }}>
                <option value="random_forest">Random Forest</option>
                <option value="svm">SVM</option>
                <option value="logistic">Logistic Regression</option>
                <option value="gradient_boost">Gradient Boost</option>
              </select>
            </div>
            <div style={card}>
              <Label>CV FOLDS</Label>
              <input type="number" value={cv} onChange={e => setCv(Number(e.target.value))} min={2} max={20} style={{ ...inputSt, marginTop: 8 }} />
            </div>
          </div>
          <Btn onClick={run} disabled={isRunning || !target}>{isRunning ? '◌ TUNING...' : '⚙️ START HYPERPARAMETER TUNING'}</Btn>
          {error && <ErrorBlock err={error} />}
          {isRunning && jobInfo && (
            <div style={card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontFamily: 'Orbitron', fontSize: 9, color: '#aa66ff' }}>{jobInfo.step || 'TUNING...'}</span>
                <span style={{ fontFamily: 'Share Tech Mono', fontSize: 10, color: '#aa66ff' }}>{jobInfo.progress || 0}%</span>
              </div>
              <div style={{ height: 6, background: 'rgba(153,51,255,0.15)', borderRadius: 3, overflow: 'hidden' }}>
                <motion.div animate={{ width: `${jobInfo.progress || 0}%` }} transition={{ duration: 0.4 }} style={{ height: '100%', background: 'linear-gradient(90deg, #9933ff, #ff66ff)', borderRadius: 3 }} />
              </div>
            </div>
          )}
          {mlTuneResult?.success && (
            <div style={{ ...card, borderColor: 'rgba(0,255,200,0.35)' }}>
              <Label style={{ color: '#00ffc8' }}>✓ TUNING COMPLETE</Label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 10 }}>
                {mlTuneResult.best_score != null && <MetricCard label="BEST SCORE" value={(mlTuneResult.best_score * 100).toFixed(2) + '%'} color="#00ffc8" />}
                {mlTuneResult.best_params && <MetricCard label="BEST PARAMS" value={JSON.stringify(mlTuneResult.best_params)} color="#ff88ff" small />}
                {mlTuneResult.n_combinations && <MetricCard label="COMBOS" value={mlTuneResult.n_combinations} color="#ffaa00" small />}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

// ─── ♻️ KFold Tab ───────────────────────────────────────────────
function KfoldTab() {
  const { mlDataset, mlKfoldResult, setMLKfoldResult } = useAtlasStore()
  const [target, setTarget] = useState('')
  const [taskType, setTaskType] = useState('classification')
  const [algorithm, setAlgorithm] = useState('random_forest')
  const [nSplits, setNSplits] = useState(5)
  const [jobId, setJobId] = useState(null)
  const [jobInfo, setJobInfo] = useState(null)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)

  useEffect(() => {
    if (!jobId) return
    pollRef.current = setInterval(async () => {
      try {
        const s = await getMLJobStatus(jobId)
        if (!s?.success) return
        setJobInfo(s)
        if (s.status === 'done') {
          clearInterval(pollRef.current); setJobId(null)
          s.result?.success ? setMLKfoldResult(s.result) : setError(s.result)
        } else if (s.status === 'error') {
          clearInterval(pollRef.current); setJobId(null); setError(s.result)
        }
      } catch {}
    }, 800)
    return () => clearInterval(pollRef.current)
  }, [jobId])

  const run = async () => {
    if (!mlDataset?.session_id || !target) return
    setError(null); setMLKfoldResult(null); setJobInfo(null)
    try {
      const res = await kfoldML({ session_id: mlDataset.session_id, target, task_type: taskType, algorithm, n_splits: nSplits })
      res.job_id ? setJobId(res.job_id) : setError(res)
    } catch { setError({ message: 'K-Fold CV failed' }) }
  }

  const allCols = mlDataset?.rawColumns || []
  const isRunning = !!jobId

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {!mlDataset && <Hint center>Upload a dataset first</Hint>}
      {mlDataset && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={card}>
              <Label>TARGET COLUMN</Label>
              <select value={target} onChange={e => setTarget(e.target.value)} style={{ ...select, marginTop: 8 }}>
                <option value="">— Select target —</option>
                {allCols.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div style={card}>
              <Label>TASK TYPE</Label>
              <select value={taskType} onChange={e => setTaskType(e.target.value)} style={{ ...select, marginTop: 8 }}>
                <option value="classification">Classification</option>
                <option value="regression">Regression</option>
              </select>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={card}>
              <Label>ALGORITHM</Label>
              <select value={algorithm} onChange={e => setAlgorithm(e.target.value)} style={{ ...select, marginTop: 8 }}>
                <option value="random_forest">Random Forest</option>
                <option value="svm">SVM</option>
                <option value="logistic">Logistic Regression</option>
                <option value="gradient_boost">Gradient Boost</option>
              </select>
            </div>
            <div style={card}>
              <Label>N SPLITS</Label>
              <input type="number" value={nSplits} onChange={e => setNSplits(Number(e.target.value))} min={2} max={20} style={{ ...inputSt, marginTop: 8 }} />
            </div>
          </div>
          <Btn onClick={run} disabled={isRunning || !target}>{isRunning ? '◌ CROSS VALIDATING...' : '♻️ RUN K-FOLD CV'}</Btn>
          {error && <ErrorBlock err={error} />}
          {isRunning && jobInfo && (
            <div style={card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontFamily: 'Orbitron', fontSize: 9, color: '#aa66ff' }}>{jobInfo.step || 'KFOLD...'}</span>
                <span style={{ fontFamily: 'Share Tech Mono', fontSize: 10, color: '#aa66ff' }}>{jobInfo.progress || 0}%</span>
              </div>
              <div style={{ height: 6, background: 'rgba(153,51,255,0.15)', borderRadius: 3, overflow: 'hidden' }}>
                <motion.div animate={{ width: `${jobInfo.progress || 0}%` }} transition={{ duration: 0.4 }} style={{ height: '100%', background: 'linear-gradient(90deg, #9933ff, #ff66ff)', borderRadius: 3 }} />
              </div>
            </div>
          )}
          {mlKfoldResult?.success && (
            <div style={{ ...card, borderColor: 'rgba(0,255,200,0.35)' }}>
              <Label style={{ color: '#00ffc8' }}>✓ K-FOLD CV COMPLETE</Label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 10 }}>
                <MetricCard label="FOLDS" value={mlKfoldResult.n_splits} color="#ff88ff" small />
                <MetricCard label="MEAN" value={(mlKfoldResult.mean_score * 100).toFixed(2) + '%'} color="#00ffc8" />
                <MetricCard label="STD" value={mlKfoldResult.std_score ? (mlKfoldResult.std_score * 100).toFixed(2) + '%' : '—'} color="#ffaa00" small />
              </div>
              {mlKfoldResult.scores && (
                <div style={{ marginTop: 12 }}>
                  <Label>PER-FOLD SCORES</Label>
                  <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6, height: 80, marginTop: 10 }}>
                    {mlKfoldResult.scores.map((s, i) => (
                      <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                        <motion.div initial={{ height: 0 }} animate={{ height: `${s * 100}px` }} transition={{ duration: 0.4, delay: i * 0.05 }}
                          style={{ width: '100%', maxWidth: 30, background: 'rgba(0,255,200,0.3)', borderRadius: '3px 3px 0 0', border: '1px solid rgba(0,255,200,0.2)' }} />
                        <span style={{ fontSize: 8, color: 'rgba(0,255,200,0.4)', fontFamily: 'Share Tech Mono', marginTop: 4 }}>Fold {i + 1}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

// ─── 🔧 FeatEng Tab ─────────────────────────────────────────────
function FeatEngTab() {
  const { mlDataset, mlFeatEngResult, setMLFeatEngResult } = useAtlasStore()
  const [operations, setOperations] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const opTypes = [
    { value: 'poly', label: 'Polynomial (x²)' },
    { value: 'interaction', label: 'Interaction (a × b)' },
    { value: 'bin', label: 'Binning (numeric → categories)' },
  ]

  const addOp = (type) => {
    setOperations(p => [...p, { type, id: Date.now() }])
  }

  const removeOp = (id) => {
    setOperations(p => p.filter(o => o.id !== id))
  }

  const run = async () => {
    if (!mlDataset?.session_id || operations.length === 0) return
    setLoading(true); setError(null); setMLFeatEngResult(null)
    try {
      const res = await featureEngineerML({ session_id: mlDataset.session_id, operations: operations.map(o => ({ type: o.type })) })
      res.success ? setMLFeatEngResult(res) : setError(res)
    } catch { setError({ message: 'Feature engineering failed' }) }
    setLoading(false)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {!mlDataset && <Hint center>Upload a dataset first</Hint>}
      {mlDataset && (
        <>
          <div style={card}>
            <Label>OPERATIONS</Label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
              {opTypes.map(op => (
                <motion.button key={op.value} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                  onClick={() => addOp(op.value)}
                  style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid rgba(0,255,200,0.2)', background: 'rgba(0,255,200,0.06)', color: '#00ffc8', fontSize: 10, fontFamily: 'Share Tech Mono', cursor: 'pointer' }}>
                  + {op.label}
                </motion.button>
              ))}
            </div>
            {operations.length === 0 && (
              <div style={{ fontSize: 10, color: 'rgba(0,255,200,0.3)', fontFamily: 'Share Tech Mono', marginTop: 8 }}>Click an operation above to add it</div>
            )}
            {operations.length > 0 && (
              <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 6 }}>
                {operations.map(op => (
                  <div key={op.id} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 10px', borderRadius: 6, background: 'rgba(0,20,16,0.5)', border: '1px solid rgba(0,255,200,0.1)' }}>
                    <span style={{ fontSize: 10, color: '#00ffc8', fontFamily: 'Share Tech Mono', flex: 1 }}>{opTypes.find(t => t.value === op.type)?.label || op.type}</span>
                    <button onClick={() => removeOp(op.id)} style={{ padding: '2px 8px', borderRadius: 4, border: '1px solid rgba(255,85,51,0.3)', background: 'transparent', color: '#ff5533', fontSize: 10, cursor: 'pointer' }}>✕</button>
                  </div>
                ))}
              </div>
            )}
          </div>
          <Btn onClick={run} disabled={loading || operations.length === 0}>
            {loading ? '◌ ENGINEERING...' : '🔧 RUN FEATURE ENGINEERING'}
          </Btn>
          {error && <ErrorBlock err={error} />}
          {mlFeatEngResult?.success && (
            <div style={{ ...card, borderColor: 'rgba(0,255,200,0.35)' }}>
              <Label style={{ color: '#00ffc8' }}>✓ FEATURE ENGINEERING COMPLETE</Label>
              <div style={{ display: 'flex', gap: 12, marginTop: 10 }}>
                <MetricCard label="ORIGINAL" value={`${mlFeatEngResult.original_shape?.[0]} x ${mlFeatEngResult.original_shape?.[1]}`} color="#ff88ff" small />
                <MetricCard label="NEW" value={`${mlFeatEngResult.new_shape?.[0]} x ${mlFeatEngResult.new_shape?.[1]}`} color="#00ffc8" small />
              </div>
              {mlFeatEngResult.new_columns && (
                <div style={{ marginTop: 12 }}>
                  <Label>NEW COLUMNS</Label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
                    {mlFeatEngResult.new_columns.map(c => (
                      <span key={c} style={{ padding: '3px 8px', borderRadius: 4, fontSize: 10, fontFamily: 'Share Tech Mono', background: 'rgba(0,170,255,0.08)', border: '1px solid rgba(0,170,255,0.2)', color: '#00aaff' }}>{c}</span>
                    ))}
                  </div>
                </div>
              )}
              {mlFeatEngResult.engineered_session_id && (
                <div style={{ marginTop: 10, fontSize: 10, color: 'rgba(0,255,200,0.4)', fontFamily: 'Share Tech Mono' }}>
                  Session: {mlFeatEngResult.engineered_session_id}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

// ─── 📋 Evaluate Tab ────────────────────────────────────────────
function EvaluateTab() {
  const { mlModels, mlDataset, mlEvaluationData, setMLEvaluationData } = useAtlasStore()
  const [selectedModel, setSelectedModel] = useState('')
  const [metric, setMetric] = useState('confusion_matrix')
  const [maxK, setMaxK] = useState(10)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const activeModels = Array.isArray(mlModels) ? mlModels : []

  const run = async () => {
    if (!selectedModel && metric !== 'elbow') return
    setLoading(true); setError(null); setMLEvaluationData(null)
    try {
      const params = { metric, session_id: mlDataset?.session_id || '' }
      if (metric === 'elbow') {
        params.max_k = maxK
      } else {
        params.model_id = selectedModel
      }
      const res = await evaluateML(params)
      res.success ? setMLEvaluationData(res) : setError(res)
    } catch { setError({ message: 'Evaluation failed' }) }
    setLoading(false)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={card}>
        <Label>METRIC</Label>
        <select value={metric} onChange={e => { setMetric(e.target.value); setMLEvaluationData(null) }} style={{ ...select, marginTop: 8 }}>
          <option value="confusion_matrix">Confusion Matrix</option>
          <option value="roc_curve">ROC Curve</option>
          <option value="elbow">Elbow Plot (Clustering)</option>
        </select>
      </div>
      {metric === 'elbow' ? (
        <div style={card}>
          <Label>MAX K</Label>
          <input type="number" value={maxK} onChange={e => setMaxK(Number(e.target.value))} min={2} max={30} style={{ ...inputSt, marginTop: 8 }} />
        </div>
      ) : (
        <div style={card}>
          <Label>SELECT MODEL</Label>
          <select value={selectedModel} onChange={e => setSelectedModel(e.target.value)} style={{ ...select, marginTop: 8 }}>
            <option value="">— Choose a trained model —</option>
            {activeModels.map(m => (
              <option key={m.model_id} value={m.model_id}>{m.model_id} ({m.size})</option>
            ))}
          </select>
        </div>
      )}
      <Btn onClick={run} disabled={loading || (metric !== 'elbow' && !selectedModel)}>
        {loading ? '◌ EVALUATING...' : '📋 RUN EVALUATION'}
      </Btn>
      {error && <ErrorBlock err={error} />}
      {mlEvaluationData?.success && metric === 'confusion_matrix' && mlEvaluationData.matrix && (
        <div style={card}>
          <Label>CONFUSION MATRIX</Label>
          {mlEvaluationData.labels && (
            <table style={{ borderCollapse: 'collapse', marginTop: 10, fontSize: 10, fontFamily: 'Share Tech Mono' }}>
              <thead>
                <tr>
                  <td style={{ padding: 4, color: 'rgba(0,255,200,0.3)' }} />
                  {mlEvaluationData.labels.map(l => (
                    <th key={l} style={{ padding: '4px 8px', color: '#00ffc8', borderBottom: '1px solid rgba(0,255,200,0.2)' }}>{l}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {mlEvaluationData.matrix.map((row, i) => (
                  <tr key={i}>
                    <td style={{ padding: '4px 8px', color: '#ff88ff', borderRight: '1px solid rgba(0,255,200,0.2)' }}>{mlEvaluationData.labels?.[i] || i}</td>
                    {row.map((v, j) => (
                      <td key={j} style={{ padding: '6px 10px', textAlign: 'center', background: v > 0 ? 'rgba(0,255,200,0.1)' : 'transparent', color: v > 0 ? '#00ffc8' : 'rgba(0,255,200,0.2)' }}>{v}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
      {mlEvaluationData?.success && metric === 'roc_curve' && mlEvaluationData.curves && (
        <div style={card}>
          <Label>ROC CURVE</Label>
          {mlEvaluationData.curves.map((curve, idx) => (
            <div key={idx}>
              <Label>{curve.label || `Class ${idx}`} {curve.auc != null && <span style={{ color: '#00ffc8' }}>(AUC: {curve.auc.toFixed(3)})</span>}</Label>
              <ROCCurve points={curve.fpr?.map((fpr, i) => ({ x: fpr, y: curve.tpr[i] })) || []} />
            </div>
          ))}
        </div>
      )}
      {mlEvaluationData?.success && metric === 'elbow' && mlEvaluationData.inertias && (
        <div style={card}>
          <Label>ELBOW PLOT</Label>
          <ElbowChart data={mlEvaluationData.inertias} />
        </div>
      )}
    </div>
  )
}

function ROCCurve({ points }) {
  if (!points || points.length === 0) return null
  const W = 280, H = 180, pad = 20
  const xMax = 1, yMax = 1
  const sx = v => v * (W - pad * 2) + pad
  const sy = v => H - pad - (v * (H - pad * 2))

  return (
    <svg width={W} height={H} style={{ marginTop: 10 }}>
      {/* Diagonal reference */}
      <line x1={sx(0)} y1={sy(0)} x2={sx(1)} y2={sy(1)} stroke="rgba(0,255,200,0.15)" strokeDasharray="3" />
      {/* Curve */}
      <polyline fill="none" stroke="#00ffc8" strokeWidth={1.5}
        points={points.map(p => `${sx(p.x)},${sy(p.y)}`).join(' ')} />
      {/* Axes */}
      <line x1={sx(0)} y1={sy(0)} x2={sx(1)} y2={sy(0)} stroke="rgba(0,255,200,0.2)" />
      <line x1={sx(0)} y1={sy(0)} x2={sx(0)} y2={sy(1)} stroke="rgba(0,255,200,0.2)" />
    </svg>
  )
}

function ElbowChart({ data }) {
  if (!data || data.length === 0) return null
  const W = 280, H = 140
  const vals = data.map(d => d.inertia ?? d)
  const kMax = vals.length + 1
  const minV = Math.min(...vals), maxV = Math.max(...vals)

  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6, height: H, marginTop: 10 }}>
      {vals.map((v, i) => (
        <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
          <motion.div initial={{ height: 0 }} animate={{ height: `${((v - minV) / (maxV - minV || 1)) * (H - 20)}px` }}
            transition={{ duration: 0.4, delay: i * 0.03 }}
            style={{ width: '100%', maxWidth: 24, background: 'rgba(0,255,200,0.3)', borderRadius: '3px 3px 0 0', border: '1px solid rgba(0,255,200,0.2)' }} />
          <span style={{ fontSize: 8, color: 'rgba(0,255,200,0.4)', fontFamily: 'Share Tech Mono', marginTop: 4 }}>k={i + 1}</span>
        </div>
      ))}
    </div>
  )
}

// ─── 🔮 Predict Tab ────────────────────────────────────────────
function PredictTab() {
  const { mlModels, mlPredictionResult, setMLPredictionResult } = useAtlasStore()
  const [selectedModel, setSelectedModel] = useState('')
  const [modelInfo, setModelInfo]         = useState(null)   // metadata from backend
  const [inputValues, setInputValues]     = useState({})
  const [loading, setLoading]             = useState(false)
  const [infoLoading, setInfoLoading]     = useState(false)
  const [error, setError]                 = useState(null)

  const activeModels = Array.isArray(mlModels) ? mlModels : []

  // Load model metadata when model changes — auto-populate feature fields
  useEffect(() => {
    if (!selectedModel) { setModelInfo(null); setInputValues({}); return }
    setInfoLoading(true)
    setInputValues({})
    setMLPredictionResult(null)
    setError(null)
    getMLModelInfo(selectedModel).then(res => {
      if (res?.success) {
        setModelInfo(res)
        // Initialise all feature fields to empty string
        const init = {}
        ;(res.features || []).forEach(f => { init[f] = '' })
        setInputValues(init)
      }
    }).catch(() => {}).finally(() => setInfoLoading(false))
  }, [selectedModel])

  const handlePredict = async () => {
    if (!selectedModel) return
    setLoading(true)
    setError(null)
    setMLPredictionResult(null)
    try {
      const res = await predictML(selectedModel, inputValues)
      if (res.success) setMLPredictionResult(res)
      else setError(res)
    } catch { setError({ message: 'Prediction failed', suggestion: 'Check all inputs are filled correctly.' }) }
    setLoading(false)
  }

  const taskColor = modelInfo?.task === 'classification' ? '#00ffc8' : modelInfo?.task === 'regression' ? '#00aaff' : '#ff88ff'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {/* Model selector */}
      <div style={card}>
        <Label>SELECT MODEL</Label>
        <select value={selectedModel} onChange={e => setSelectedModel(e.target.value)} style={{ ...select, marginTop: 8 }}>
          <option value="">— Choose a trained model —</option>
          {activeModels.map(m => (
            <option key={m.model_id} value={m.model_id}>
              {m.task ? `[${m.task}] ` : ''}{m.model_id} ({m.size})
            </option>
          ))}
        </select>
      </div>

      {/* Model info badge */}
      {modelInfo && (
        <div style={{ ...card, display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center' }}>
          <span style={{ padding: '3px 10px', borderRadius: 4, fontSize: 10, fontFamily: 'Share Tech Mono', background: `${taskColor}15`, border: `1px solid ${taskColor}44`, color: taskColor }}>
            {modelInfo.task}
          </span>
          <span style={{ fontSize: 10, color: 'rgba(0,255,200,0.5)', fontFamily: 'Share Tech Mono' }}>
            Target: <span style={{ color: '#00ffc8' }}>{modelInfo.target}</span>
          </span>
          {modelInfo.accuracy != null && (
            <span style={{ fontSize: 10, color: 'rgba(0,255,200,0.5)', fontFamily: 'Share Tech Mono' }}>
              Accuracy: <span style={{ color: '#00ffc8' }}>{(modelInfo.accuracy * 100).toFixed(1)}%</span>
            </span>
          )}
          {modelInfo.rmse != null && (
            <span style={{ fontSize: 10, color: 'rgba(0,170,255,0.5)', fontFamily: 'Share Tech Mono' }}>
              RMSE: <span style={{ color: '#00aaff' }}>{modelInfo.rmse}</span>
            </span>
          )}
        </div>
      )}

      {infoLoading && <StatusLine text="Loading model info..." />}

      {/* Auto-populated feature inputs */}
      {modelInfo && Object.keys(inputValues).length > 0 && (
        <div style={card}>
          <Label>INPUT FEATURES</Label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 8, marginTop: 8 }}>
            {Object.entries(inputValues).map(([key, val]) => {
              const dtype = modelInfo.feature_types?.[key] || ''
              return (
                <div key={key}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                    <span style={{ fontSize: 9, color: 'rgba(0,255,200,0.6)', fontFamily: 'Share Tech Mono' }}>{key}</span>
                    {dtype && <span style={{ fontSize: 8, color: 'rgba(0,255,200,0.3)', fontFamily: 'Share Tech Mono' }}>{dtype}</span>}
                  </div>
                  <input
                    value={val}
                    onChange={e => setInputValues(p => ({ ...p, [key]: e.target.value }))}
                    placeholder={dtype.includes('int') ? '0' : dtype.includes('float') ? '0.0' : '…'}
                    style={inputSt}
                  />
                </div>
              )
            })}
          </div>
        </div>
      )}

      {selectedModel && !infoLoading && (
        <Btn onClick={handlePredict} disabled={loading}>
          {loading ? '◌ PREDICTING...' : '🔮 PREDICT'}
        </Btn>
      )}
      {error && <ErrorBlock err={error} />}

      {/* Result */}
      {mlPredictionResult?.success && (
        <div style={{ ...card, borderColor: 'rgba(0,255,200,0.35)' }}>
          <Label style={{ color: '#00ffc8' }}>✓ PREDICTION RESULT</Label>
          <div style={{ fontSize: 32, color: '#00ffc8', fontFamily: 'Share Tech Mono', marginTop: 8 }}>
            {String(mlPredictionResult.prediction)}
          </div>
          {mlPredictionResult.confidence != null && (
            <div style={{ marginTop: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span style={{ fontSize: 9, color: 'rgba(0,255,200,0.5)', fontFamily: 'Orbitron', letterSpacing: 1 }}>CONFIDENCE</span>
                <span style={{ fontSize: 10, color: '#00ffc8', fontFamily: 'Share Tech Mono' }}>{(mlPredictionResult.confidence * 100).toFixed(1)}%</span>
              </div>
              <div style={{ height: 8, background: 'rgba(0,255,200,0.08)', borderRadius: 4, overflow: 'hidden' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(mlPredictionResult.confidence * 100).toFixed(0)}%` }}
                  transition={{ duration: 0.8, ease: 'easeOut' }}
                  style={{ height: '100%', background: 'linear-gradient(90deg, #00ffc8, #00aaff)', borderRadius: 4 }} />
              </div>
            </div>
          )}
          {/* Probability breakdown */}
          {mlPredictionResult.probabilities && (
            <div style={{ marginTop: 12 }}>
              <Label>CLASS PROBABILITIES</Label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>
                {Object.entries(mlPredictionResult.probabilities).map(([cls, prob]) => (
                  <span key={cls} style={{ padding: '3px 10px', borderRadius: 4, fontSize: 10, fontFamily: 'Share Tech Mono', background: 'rgba(0,255,200,0.06)', border: '1px solid rgba(0,255,200,0.2)', color: '#00ffc8' }}>
                    {cls}: {(prob * 100).toFixed(1)}%
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── 📦 Models Tab ─────────────────────────────────────────────
function ModelsTab() {
  const { mlModels, setMLModels } = useAtlasStore()
  const [loading, setLoading]     = useState(false)

  const refresh = async () => {
    setLoading(true)
    try {
      const res = await listMLModels()
      if (res?.success) setMLModels(res.models)
    } catch {}
    setLoading(false)
  }

  const handleDelete = async (id) => {
    if (!window.confirm(`Delete model "${id}"?`)) return
    try { await deleteMLModel(id); refresh() } catch {}
  }

  const modelList = Array.isArray(mlModels) ? mlModels : []

  const cols = [
    { name: 'MODEL', selector: r => r.model_id, sortable: true, grow: 2,
      cell: r => <span style={{ fontFamily: 'Share Tech Mono', fontSize: 10, color: '#00ffc8', wordBreak: 'break-all' }}>{r.model_id}</span> },
    { name: 'TASK', selector: r => r.task, sortable: true, width: '110px',
      cell: r => {
        const c = r.task === 'classification' ? '#00ffc8' : r.task === 'regression' ? '#00aaff' : '#ff88ff'
        return <span style={{ fontSize: 10, fontFamily: 'Share Tech Mono', color: c }}>{r.task || '—'}</span>
      }
    },
    { name: 'SCORE', selector: r => r.accuracy ?? r.rmse, sortable: true, width: '90px',
      cell: r => {
        if (r.accuracy != null) return <span style={{ fontFamily: 'Share Tech Mono', fontSize: 10, color: '#00ffc8' }}>{(r.accuracy * 100).toFixed(1)}%</span>
        if (r.rmse    != null) return <span style={{ fontFamily: 'Share Tech Mono', fontSize: 10, color: '#00aaff' }}>RMSE {r.rmse}</span>
        return <span style={{ color: 'rgba(0,255,200,0.3)', fontSize: 10 }}>—</span>
      }
    },
    { name: 'SIZE', selector: r => r.size, width: '80px',
      cell: r => <span style={{ fontFamily: 'Share Tech Mono', fontSize: 10, color: 'rgba(0,255,200,0.5)' }}>{r.size}</span> },
    { name: '', width: '80px', ignoreRowClick: true,
      cell: r => (
        <button onClick={() => handleDelete(r.model_id)}
          style={{ padding: '4px 10px', borderRadius: 4, border: '1px solid rgba(255,85,51,0.3)', background: 'rgba(255,85,51,0.08)', color: '#ff5533', fontSize: 10, cursor: 'pointer', fontFamily: 'Rajdhani' }}>
          DELETE
        </button>
      )
    },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <Btn onClick={refresh} disabled={loading}>{loading ? '◌ REFRESHING...' : '🔄 REFRESH'}</Btn>
        <span style={{ fontSize: 10, color: 'rgba(0,255,200,0.4)', fontFamily: 'Share Tech Mono' }}>
          {modelList.length} model{modelList.length !== 1 ? 's' : ''}
        </span>
      </div>
      <div style={card}>
        {modelList.length === 0
          ? <Hint center>No trained models yet — go to TRAIN to create one</Hint>
          : <DataTable columns={cols} data={modelList} customStyles={tableStyles} pagination paginationPerPage={10} highlightOnHover dense />
        }
      </div>
    </div>
  )
}

// ─── 📈 Visualize Tab ──────────────────────────────────────────
function VisualizeTab() {
  const { mlDataset, mlPlotData, setMLPlotData } = useAtlasStore()
  const [plotType, setPlotType]     = useState('histogram')
  const [selectedCols, setSelectedCols] = useState([])
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState(null)

  const allCols    = mlDataset?.rawColumns || []
  const numericCols = mlDataset?.dtypes
    ? Object.entries(mlDataset.dtypes).filter(([, t]) => t.includes('int') || t.includes('float')).map(([c]) => c)
    : []

  const generate = async () => {
    if (!mlDataset?.session_id) return
    setLoading(true)
    setError(null)
    setMLPlotData(null)
    try {
      const res = await getMLChartData({
        session_id: mlDataset.session_id,
        plot_type: plotType,
        columns: selectedCols.length > 0 ? selectedCols : undefined,
      })
      if (res.success) setMLPlotData(res)
      else setError(res)
    } catch { setError({ message: 'Chart generation failed', suggestion: 'Check dataset is still loaded.' }) }
    setLoading(false)
  }

  const toggleCol = col =>
    setSelectedCols(p => p.includes(col) ? p.filter(c => c !== col) : [...p, col])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {!mlDataset && <Hint center>Upload a dataset first</Hint>}

      {mlDataset && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={card}>
              <Label>PLOT TYPE</Label>
              <select value={plotType} onChange={e => { setPlotType(e.target.value); setSelectedCols([]) }} style={{ ...select, marginTop: 8 }}>
                <option value="histogram">📊 Histogram</option>
                <option value="scatter">🔵 Scatter</option>
                <option value="correlation">🔥 Correlation</option>
                <option value="boxplot">📦 Box Plot</option>
                <option value="bar">📊 Bar Chart</option>
              </select>
            </div>
            <div style={card}>
              <Label>COLUMNS</Label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 8 }}>
                {(plotType === 'bar' ? allCols : numericCols).map(col => (
                  <span key={col} onClick={() => toggleCol(col)} style={{
                    padding: '3px 8px', borderRadius: 4, fontSize: 10, fontFamily: 'Share Tech Mono', cursor: 'pointer',
                    background: selectedCols.includes(col) ? 'rgba(0,255,200,0.15)' : 'rgba(0,255,200,0.04)',
                    border: `1px solid ${selectedCols.includes(col) ? 'rgba(0,255,200,0.5)' : 'rgba(0,255,200,0.15)'}`,
                    color: selectedCols.includes(col) ? '#00ffc8' : 'rgba(0,255,200,0.4)',
                    transition: 'all 0.15s'
                  }}>
                    {col}
                  </span>
                ))}
                {numericCols.length === 0 && plotType !== 'bar' && <Hint>No numeric columns</Hint>}
              </div>
            </div>
          </div>

          <Btn onClick={generate} disabled={loading}>
            {loading ? '◌ GENERATING...' : '📈 GENERATE CHART'}
          </Btn>
          {error && <ErrorBlock err={error} />}

          {/* Inline chart render */}
          {mlPlotData && <ChartRenderer data={mlPlotData} />}
        </>
      )}
    </div>
  )
}

// ─── Chart Renderer (frontend-side, no images) ─────────────────
function ChartRenderer({ data }) {
  if (!data) return null

  const BAR_COLOR = '#00ffc8'
  const MAX_BAR_W = 280

  if (data.plot_type === 'histogram') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {Object.entries(data.data || {}).map(([col, { bins, counts }]) => {
          const max = Math.max(...counts, 1)
          return (
            <div key={col} style={card}>
              <Label>{col} — HISTOGRAM</Label>
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, height: 80, marginTop: 10, overflowX: 'auto' }}>
                {counts.map((c, i) => (
                  <motion.div key={i}
                    initial={{ height: 0 }} animate={{ height: `${(c / max) * 100}%` }}
                    transition={{ duration: 0.4, delay: i * 0.01 }}
                    title={`${bins[i]?.toFixed(2)}: ${c}`}
                    style={{ flex: 1, minWidth: 4, background: BAR_COLOR, borderRadius: '2px 2px 0 0', opacity: 0.75, cursor: 'default' }} />
                ))}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9, color: 'rgba(0,255,200,0.3)', fontFamily: 'Share Tech Mono', marginTop: 2 }}>
                <span>{bins[0]?.toFixed(2)}</span>
                <span>{bins[bins.length - 1]?.toFixed(2)}</span>
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  if (data.plot_type === 'bar') {
    const max = Math.max(...(data.data || []).map(d => d.count), 1)
    return (
      <div style={card}>
        <Label>{data.label} — BAR CHART</Label>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 5, marginTop: 10 }}>
          {(data.data || []).map(({ name, count }) => (
            <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 10, color: 'rgba(0,255,200,0.5)', fontFamily: 'Share Tech Mono', width: 90, textAlign: 'right', flexShrink: 0 }}>{name}</span>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(count / max) * MAX_BAR_W}px` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                style={{ height: 16, background: 'rgba(0,255,200,0.3)', borderRadius: 3, border: '1px solid rgba(0,255,200,0.2)' }} />
              <span style={{ fontSize: 10, color: '#00ffc8', fontFamily: 'Share Tech Mono' }}>{count}</span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (data.plot_type === 'boxplot') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {Object.entries(data.data || {}).map(([col, stats]) => (
          <div key={col} style={card}>
            <Label>{col} — BOX PLOT</Label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 8 }}>
              {[
                { label: 'MIN',    value: stats.min,    color: '#ff5533' },
                { label: 'Q1',     value: stats.q1,     color: '#ffaa00' },
                { label: 'MEDIAN', value: stats.median, color: '#00ffc8' },
                { label: 'Q3',     value: stats.q3,     color: '#ffaa00' },
                { label: 'MAX',    value: stats.max,    color: '#ff5533' },
              ].map(({ label, value, color }) => (
                <div key={label} style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 8, color: 'rgba(0,255,200,0.4)', fontFamily: 'Orbitron', letterSpacing: 1 }}>{label}</div>
                  <div style={{ fontSize: 13, color, fontFamily: 'Share Tech Mono', marginTop: 2 }}>{Number(value).toFixed(3)}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (data.plot_type === 'scatter') {
    const pts = data.data || []
    const xs  = pts.map(p => p.x)
    const ys  = pts.map(p => p.y)
    const xMin = Math.min(...xs), xMax = Math.max(...xs)
    const yMin = Math.min(...ys), yMax = Math.max(...ys)
    const W = 280, H = 160
    const px = x => ((x - xMin) / (xMax - xMin || 1)) * W
    const py = y => H - ((y - yMin) / (yMax - yMin || 1)) * H

    return (
      <div style={card}>
        <Label>{data.x_label} vs {data.y_label} — SCATTER</Label>
        <svg width={W} height={H} style={{ marginTop: 10, overflow: 'visible' }}>
          {pts.slice(0, 500).map((p, i) => (
            <circle key={i} cx={px(p.x)} cy={py(p.y)} r={2.5}
              fill="rgba(0,255,200,0.45)" stroke="none" />
          ))}
        </svg>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9, color: 'rgba(0,255,200,0.3)', fontFamily: 'Share Tech Mono', marginTop: 2 }}>
          <span>{xMin.toFixed(2)}</span>
          <span>{xMax.toFixed(2)}</span>
        </div>
      </div>
    )
  }

  if (data.plot_type === 'correlation') {
    const cols = data.columns || []
    const byPair = {}
    ;(data.data || []).forEach(({ row, col, value }) => { byPair[`${row}||${col}`] = value })
    const heat = v => {
      const a = Math.abs(v)
      if (v > 0.6)  return `rgba(0,255,200,${0.3 + a * 0.5})`
      if (v < -0.6) return `rgba(255,85,51,${0.3 + a * 0.5})`
      return `rgba(255,255,255,${a * 0.2})`
    }
    const cellW = Math.min(54, Math.floor(320 / (cols.length + 1)))

    return (
      <div style={{ ...card, overflowX: 'auto' }}>
        <Label>CORRELATION MATRIX</Label>
        <table style={{ borderCollapse: 'collapse', marginTop: 10, fontSize: 9, fontFamily: 'Share Tech Mono' }}>
          <thead>
            <tr>
              <td style={{ width: cellW }} />
              {cols.map(c => <th key={c} style={{ width: cellW, color: 'rgba(0,255,200,0.5)', padding: '2px 3px', textAlign: 'center', fontSize: 8, overflow: 'hidden', maxWidth: cellW }}>{c.slice(0, 6)}</th>)}
            </tr>
          </thead>
          <tbody>
            {cols.map(row => (
              <tr key={row}>
                <td style={{ color: 'rgba(0,255,200,0.5)', fontSize: 8, paddingRight: 4, textAlign: 'right', maxWidth: cellW, overflow: 'hidden' }}>{row.slice(0, 6)}</td>
                {cols.map(col => {
                  const v = byPair[`${row}||${col}`] ?? 0
                  return (
                    <td key={col} title={`${row} × ${col}: ${v.toFixed(3)}`}
                      style={{ width: cellW, height: cellW, background: heat(v), textAlign: 'center', fontSize: 8, color: '#fff', border: '1px solid rgba(0,255,200,0.06)' }}>
                      {v.toFixed(2)}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  return <div style={{ ...card, color: 'rgba(0,255,200,0.4)', fontSize: 11 }}>Unknown chart type: {data.plot_type}</div>
}

// ─── Shared micro-components ────────────────────────────────────
function Label({ children, style }) {
  return <div style={{ fontFamily: 'Orbitron', fontSize: 9, letterSpacing: 2, color: 'var(--text-dim, rgba(0,255,200,0.45))', ...style }}>{children}</div>
}
function Stat({ label, value, color = '#00ffc8' }) {
  return (
    <div style={{ textAlign: 'right' }}>
      <div style={{ fontSize: 8, color: 'rgba(0,255,200,0.4)', fontFamily: 'Orbitron', letterSpacing: 1 }}>{label}</div>
      <div style={{ fontSize: 12, color, fontFamily: 'Share Tech Mono' }}>{value}</div>
    </div>
  )
}
function Hint({ children, center }) {
  return <div style={{ color: 'rgba(0,255,200,0.3)', fontSize: 11, fontFamily: 'Share Tech Mono', textAlign: center ? 'center' : undefined, padding: center ? 20 : undefined }}>{children}</div>
}
function StatusLine({ text }) {
  return <div style={{ textAlign: 'center', color: '#00ffc8', fontSize: 12, fontFamily: 'Share Tech Mono' }}>◌ {text}</div>
}
function Btn({ children, onClick, disabled }) {
  return (
    <motion.button whileHover={disabled ? {} : { scale: 1.02 }} whileTap={disabled ? {} : { scale: 0.95 }}
      onClick={onClick} disabled={disabled}
      style={{ ...btnSt, opacity: disabled ? 0.5 : 1, cursor: disabled ? 'not-allowed' : 'pointer', alignSelf: 'flex-start' }}>
      {children}
    </motion.button>
  )
}
function ErrorBlock({ err }) {
  if (!err) return null
  const msg  = err.message || String(err)
  const hint = err.suggestion
  return (
    <div style={{ background: 'rgba(255,85,51,0.06)', border: '1px solid rgba(255,85,51,0.25)', borderRadius: 8, padding: '10px 14px' }}>
      <div style={{ color: '#ff5533', fontSize: 12, fontFamily: 'Share Tech Mono' }}>❌ {msg}</div>
      {hint && <div style={{ color: 'rgba(255,170,100,0.8)', fontSize: 11, fontFamily: 'Share Tech Mono', marginTop: 4 }}>💡 {hint}</div>}
    </div>
  )
}
function MetricCard({ label, value, color, small }) {
  return (
    <div style={{ background: 'rgba(0,20,16,0.5)', border: `1px solid ${color}22`, borderRadius: 8, padding: 10 }}>
      <div style={{ fontFamily: 'Orbitron', fontSize: 8, letterSpacing: 1, color: 'rgba(0,255,200,0.35)', marginBottom: 4 }}>{label}</div>
      <div style={{ fontFamily: 'Share Tech Mono', fontSize: small ? 11 : 18, color, wordBreak: 'break-all' }}>{value}</div>
    </div>
  )
}

// ─── Shared style tokens ────────────────────────────────────────
const card = {
  background: 'rgba(0,20,16,0.7)', border: '1px solid rgba(0,255,200,0.15)',
  borderRadius: 10, padding: 14
}
const btnSt = {
  padding: '10px 18px', borderRadius: 8, border: '1px solid rgba(0,255,200,0.25)',
  background: 'rgba(0,255,200,0.08)', color: '#00ffc8',
  fontFamily: 'Rajdhani', fontSize: 12, letterSpacing: 1, transition: 'all 0.2s'
}
const select = {
  width: '100%', padding: '8px 10px', borderRadius: 6,
  border: '1px solid rgba(0,255,200,0.2)', background: 'rgba(0,20,16,0.8)',
  color: '#00ffc8', fontFamily: 'Share Tech Mono, monospace', fontSize: 11,
  outline: 'none', cursor: 'pointer'
}
const inputSt = {
  width: '100%', padding: '8px 10px', borderRadius: 6, boxSizing: 'border-box',
  border: '1px solid rgba(0,255,200,0.2)', background: 'rgba(0,20,16,0.8)',
  color: '#00ffc8', fontFamily: 'Share Tech Mono, monospace', fontSize: 11,
  outline: 'none'
}