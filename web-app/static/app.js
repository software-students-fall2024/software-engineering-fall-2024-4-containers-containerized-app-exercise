function analyzeSentence() {
  const sentence = document.getElementById('sentenceInput').value;

  fetch('/checkSentiment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sentence })
  })
  .then(response => response.json())
  .then(data => {
      const requestId = data.request_id;
      // Keep checking until the analysis is available
      fetchAnalysisWithRetry(requestId, 10);  // Max retries: 10
  })
  .catch(error => console.error('Error:', error));
}

function displaySentiment(analysis) {
  const visualization = document.getElementById('visualization');
  visualization.textContent = `Sentiment: ${analysis}`;
}

// Speech recognition
function startDictation() {
  if ('webkitSpeechRecognition' in window) {

      const recognition = new webkitSpeechRecognition();

      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.lang = 'en-US';
      recognition.start();

      recognition.onresult = function(e) {
          document.getElementById('sentenceInput').value = e.results[0][0].transcript;
          recognition.stop();
      };

      recognition.onerror = function(e) {
          recognition.stop();
      };
  } else {
      alert('Speech recognition not supported in this browser.');
  }
}

function fetchAnalysisWithRetry(requestId, retries) {
  if (retries <= 0) {
      console.error("Failed to retrieve analysis after multiple attempts");
      return;
  }

  setTimeout(() => {
      fetch(`/get_analysis?request_id=${requestId}`)
          .then(response => response.json())
          .then(data => {
              if (data.message) {
                  console.error(data.message);
                  // Retry if no analysis found yet
                  fetchAnalysisWithRetry(requestId, retries - 1);
              } else {
                  visualizeSentimentAnalysis(data);
              }
          })
          .catch(error => {
              console.error('Error:', error);
              fetchAnalysisWithRetry(requestId, retries - 1);
          });
  }, 10000);  // Increased retry interval to 10 seconds
}


function visualizeSentimentAnalysis(data) {
  const sentimentTrend = data.sentiment_trend;
  
  // Clear previous visualization
  d3.select("#visualization").selectAll("*").remove();

  // Set dimensions and margins for the chart
  const width = 600;
  const height = 300;
  const margin = { top: 20, right: 30, bottom: 50, left: 40 };

  // Create the SVG element
  const svg = d3.select("#visualization")
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

  // Create scales
  const x = d3.scaleLinear()
      .domain([0, d3.max(sentimentTrend, d => d.sentence_index)])
      .range([0, width]);

  const y = d3.scaleLinear()
      .domain([-1, 1])  // Compound score ranges from -1 to 1
      .range([height, 0]);

  // Add X axis
  svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x));

  // Add Y axis
  svg.append("g")
      .call(d3.axisLeft(y));

  // Add line path for sentiment trend
  svg.append("path")
      .datum(sentimentTrend)
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 1.5)
      .attr("d", d3.line()
          .x(d => x(d.sentence_index))
          .y(d => y(d.compound))
      );

  // Add points to the line
  svg.selectAll("dot")
      .data(sentimentTrend)
      .enter()
      .append("circle")
      .attr("cx", d => x(d.sentence_index))
      .attr("cy", d => y(d.compound))
      .attr("r", 4)
      .attr("fill", "steelblue");
}

function visualizeSentimentDistribution(data) {
  const sentimentCounter = {
      "positive": 0,
      "negative": 0,
      "neutral": 0
  };

  data.sentences.forEach(sentence => {
      const compound = sentence.analysis.compound;
      if (compound > 0.05) sentimentCounter.positive++;
      else if (compound < -0.05) sentimentCounter.negative++;
      else sentimentCounter.neutral++;
  });

  // Prepare data for pie chart
  const pieData = Object.entries(sentimentCounter).map(([label, value]) => ({ label, value }));

  // Render pie chart using D3.js
  const width = 300;
  const height = 300;
  const radius = Math.min(width, height) / 2;

  const svg = d3.select("#visualization")
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2},${height / 2})`);

  const pie = d3.pie()
      .value(d => d.value);

  const arc = d3.arc()
      .innerRadius(0)
      .outerRadius(radius);

  svg.selectAll('arc')
      .data(pie(pieData))
      .enter()
      .append('path')
      .attr('d', arc)
      .attr('fill', d => {
          if (d.data.label === "positive") return "#4caf50";
          if (d.data.label === "negative") return "#f44336";
          return "#ffc107";
      });
}

function visualizeEmotionDistribution(data) {
  const emotionCounter = {};

  data.sentences.forEach(sentence => {
      sentence.emotions.forEach(emotion => {
          if (!emotionCounter[emotion]) {
              emotionCounter[emotion] = 0;
          }
          emotionCounter[emotion]++;
      });
  });

  const emotions = Object.keys(emotionCounter);
  const counts = Object.values(emotionCounter);

  // Render bar chart using D3.js
  const width = 500;
  const height = 300;
  const margin = { top: 20, right: 30, bottom: 40, left: 50 };

  const svg = d3.select("#visualization")
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3.scaleBand()
      .domain(emotions)
      .range([0, width])
      .padding(0.2);

  const y = d3.scaleLinear()
      .domain([0, d3.max(counts)])
      .nice()
      .range([height, 0]);

  svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x));

  svg.append("g")
      .call(d3.axisLeft(y));

  svg.selectAll(".bar")
      .data(emotions)
      .enter()
      .append("rect")
      .attr("class", "bar")
      .attr("x", d => x(d))
      .attr("width", x.bandwidth())
      .attr("y", d => y(emotionCounter[d]))
      .attr("height", d => height - y(emotionCounter[d]))
      .attr("fill", "#007bff");
}

function redoAnalysis() {
  document.getElementById('sentenceInput').value = '';
  d3.select("#visualization").selectAll("*").remove();
}