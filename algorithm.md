```mermaid
%%{init: {
  "theme": "default",
  "flowchart": {
    "useMaxWidth": false,
    "nodeSpacing": 60,
    "rankSpacing": 60
  }
}}%%
flowchart LR

    subgraph Navigation
        direction TB
        navEntry(("Navigation"))        
        a -->|Yes| b{Junction Detected?}
        b -->|Yes| c[Perform Route Action]
        c --> d[Route Dictionary]
        b -->|No| g[Line Following]
        g --> t[2 sensors ~ line width]

        subgraph Line_Following
            direction TB
            t --> u[If one detects white line]
            u --> v[Slightly turn opposite direction]
        end

        subgraph Routes
            direction TB
            d --> e[Lists of Routes]
            e -->|each route| f["a list of steps#91;#91;#40;x,x#41;,lambda:action_function/None#93;,...#93;#40;x=0,1#41;#93;"]
        end
    end

    I --> J[Loop 4 Times]
    subgraph Pickup
    direction TB
    h --> i{Distance >= Safety?}
    i -->|Yes| j[Line Following]
    j --> |No| w[QR Code detected?]
    w --> |Yes|k[Retract Actuator]
    w --> |No|x[reverse a certain distance, try again]
    x -->|attempts<3|i
    x -->|attempts>3|y[Assign a random destination]
    y -->k
    k --> l{Last Block?}
    l -->|Yes| m[Reverse Distance]
    l -->|No| n[Rotate 180]
    n --> navEntry
    end
    subgraph Dropoff
        direction TB
        o --> p[Extend Actuator]
        p --> q[Reverse]
        q --> r[Rotate 180]
        r --> navEntry
    end
    subgraph MainLoop
        direction TB
        A[Main Program Start] --> D[System Initialization]
        D --> E{Button Pressed?}
        E -->|No| E
        E -->|Yes| F[Record Start Time]
        F --> G[Retract Actuator]
        G --> H[Start LED Flashing]
        H --> I[Navigate to D1]
        I --> a[While in route]
        J --> K[Pickup Operation]
        K --> h[Extend Actuator]
        K --> L[Navigate to Destination]
        L --> M[Drop-off Operation]
        M --> o[Forward some distance]

        M --> N{Last Iteration?}
        N -->|No| O[Return to D1]
        N -->|Yes| P{Time < 4min?}
        O --> J
        P -->|Yes| Q[Navigate to D2]
        Q --> R[Final Pickup]
        R --> S[Navigate to A]
        S --> T[Drop-off at A]
        T --> U[Return to Start]
    
        P -->|No| V[Navigate Final Route]
    
        U --> W[Forward 1.8s]
        V --> W
        W --> X[Turn Off LED]
        X --> Y[Stop All Motors]
        Y --> Z[Program End]
    end



    classDef critical fill:#ffebee,stroke:#c62828;
    class E,K,M,P,Q,R,S,T critical;

