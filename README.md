![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.

## ML result
```json
[{
  "request_id": "2ca1c4d9-9f77-42a1-814d-be5f721408d0",
  "sentences": [
    {
      "sentence": "With an apology and full back pay.",
      "status": "processed",
      "analysis": {
        "neg": 0.184,
        "neu": 0.658,
        "pos": 0.158,
        "compound": -0.0516
      },
      "emotions": [
        "Sad"
      ]
    },
    {
      "sentence": "Thank you.",
      "status": "processed",
      "analysis": {
        "neg": 0,
        "neu": 0.286,
        "pos": 0.714,
        "compound": 0.3612
      },
      "emotions": [
        "Neutural"
      ]
    },
    {
      "sentence": "And they deserve an apology and they deserve full back pay and they'll get it.",
      "status": "processed",
      "analysis": {
        "neg": 0.09,
        "neu": 0.833,
        "pos": 0.077,
        "compound": -0.0516
      },
      "emotions": [
        "Sad"
      ]
    },
    {
      "sentence": "And unlike Biden, possibly getting us into World War III, which can seriously happen, I will keep America out of foolish and unnecessary foreign wars just as I did for four straight years.",
      "status": "processed",
      "analysis": {
        "neg": 0.288,
        "neu": 0.663,
        "pos": 0.048,
        "compound": -0.8555
      },
      "emotions": [
        "Fear"
      ]
    },
    {
      "sentence": "We will again have peace through strength.",
      "status": "processed",
      "analysis": {
        "neg": 0,
        "neu": 0.427,
        "pos": 0.573,
        "compound": 0.7717
      },
      "emotions": [
        "Neutural"
      ]
    },
    {
      "sentence": "That's all it is.",
      "status": "processed",
      "analysis": {
        "neg": 0,
        "neu": 1,
        "pos": 0,
        "compound": 0
      },
      "emotions": [
        "Neutural"
      ]
    },
    {
      "sentence": "(51:45) As events oversees have shown to protect our people from the unthinkable thread of nuclear weapons and hypersonic missiles, the United States must also build a state of the art next generation missile defense shield.",
      "status": "processed",
      "analysis": {
        "neg": 0.071,
        "neu": 0.76,
        "pos": 0.169,
        "compound": 0.4588
      },
      "emotions": [
        "Fear"
      ]
    },
    ...
  ],
  "overall_status": "processed",
  "timestamp": {
    "$date": "2024-11-12T02:23:46.522Z"
  },
  "overall_emotions": [
    "Neutural"
  ],
  "sentiment_trend": [
    {
      "sentence_index": 0,
      "compound": -0.0516
    },
    {
      "sentence_index": 1,
      "compound": 0.3612
    },
    {
      "sentence_index": 2,
      "compound": -0.0516
    },
    ...
  ],
  "summary": "That's all it is. You had a winner, you had a loser. They... And I appreciate the job you do and the abuse that you've taken. We will be resisted by the combined forces of the establishment, the media, the special interest, the globalists, the Marxist, radicals, the woke corporations, the weaponized power of the federal government, the colossal political machines, the tidal wave of dark money and the most dangerous domestic censorship system ever created by man or woman. If our movement remains united and confident, then we will shatter the forces of tyranny and we will unleash that glories of liberty for ourselves and for our children, and for generations yet to come.",
  "topics": [
    [
      0,
      "0.250*\"country\" + 0.201*\"wa\" + 0.176*\"need\" + 0.176*\"thank\""
    ],
    [
      1,
      "0.342*\"america\" + 0.307*\"make\" + 0.232*\"election\" + 0.045*\"great\""
    ],
    [
      2,
      "0.486*\"got\" + 0.347*\"year\" + 0.018*\"america\" + 0.014*\"country\""
    ],
    [
      3,
      "0.419*\"people\" + 0.418*\"great\" + 0.014*\"thank\" + 0.014*\"election\""
    ],
    [
      4,
      "0.404*\"stand\" + 0.404*\"congress\" + 0.020*\"year\" + 0.016*\"wa\""
    ]
  ]
}]
```