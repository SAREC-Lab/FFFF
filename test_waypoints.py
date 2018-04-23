import matplotlib.pyplot as plt

unscaled_path =  [[41.71477164654061, -86.24215149367228], [41.71479083690792, -86.24214081745595], [41.714805393479764, -86.24212437495589], [41.71481366455555, -86.24210403161123], [41.71481519239023, -86.24208999983966], [41.71481519239023, -86.24178999988362], [41.71481149364263, -86.24176835315302], [41.714800817426294, -86.24174916278571], [41.71478437492624, -86.24173460621387], [41.71476403158158, -86.24172633513808], [41.71474999981001, -86.2417248073034], [41.71461999975145, -86.2417248073034], [41.71459835302085, -86.241728506051], [41.714579162653536, -86.24173918226734], [41.714564606081694, -86.24175562476739], [41.71455633500591, -86.24177596811205], [41.714554807171226, -86.24178999988362], [41.714554807171226, -86.24208999983966], [41.71455850591883, -86.24211164657027], [41.714569182135165, -86.24213083693758], [41.71458562463522, -86.24214539350942], [41.71460596797988, -86.2421536645852], [41.71461999975145, -86.24215519241989], [41.71474999981001, -86.24215519241989]]
leader_waypoints = [
    [
      41.71462,
      -86.24179,
      10
    ],
    [
      41.71462,
      -86.24209,
      10
    ],
    [
      41.71475,
      -86.24209,
      10
    ],
    [
      41.71475,
      -86.24179,
      10
    ],
    [
      41.71462,
      -86.24179,
      10
    ]
  ]
leader_x = []
leader_y = []

for waypoint in leader_waypoints:
    leader_x.append(waypoint[0])
    leader_y.append(waypoint[1])


follower1_x = []
follower1_y = []
for waypoint in unscaled_path:
    follower1_x.append(waypoint[0])
    follower1_y.append(waypoint[1])

for i in range(0, len(leader_x)):
    plt.plot(leader_x[i:i+2], leader_y[i:i+2], 'ro-')

for i in range(0, len(follower1_x)):
    plt.plot(follower1_x[i:i+2], follower1_y[i:i+2], 'go-')

plt.show()