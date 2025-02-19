```mermaid
flowchart LR
    A[Main Program Start] --> D[System Initialization]
    D --> E{Button Pressed?}
    E -->|No| E
    E -->|Yes| F[Record Start Time]
    F --> G[Retract Actuator]
    G --> H[Start LED Flashing]
    H --> I[Navigate to D1]

    subgraph Navigation
        direction TB
        I --> a[While in route]
        a -->|Yes| b{Junction Detected?}
        b -->|Yes| c[Perform Route Action]
        b -->|No| g[Line Following]

        subgraph Line_Following
            direction TB
            g --> t[2 sensors ~ line width]
            t --> u[If one detects white line]
            u --> v[Slightly turn opposite direction]
        end

        subgraph Routes
            direction TB
            c --> d[Route Dictionary]
            d --> e[Lists of Routes]
            e -->|each route| f[each route--a list of steps&#91;&quot;&#91;&#40;x,x&#41;,lambda:action_function/None&#93;,...&#93;&#40;x=0,1&#41;&quot;&#93;]
        end
    end

    I --> J[Loop 4 Times]

    subgraph MainLoop
        direction TB
        J --> K[Pickup Operation]
        subgraph Pickup
            direction TB
            K --> h[Extend Actuator]
            h --> i{Distance >= Safety?}
            i -->|Yes| j[Line Following]
            j --> k[Retract Actuator]
            k --> l{Last Block?}
            l -->|Yes| m[Reverse Distance]
            l -->|No| n[Rotate 180]
            n --> K
        end

        K --> L[Navigate to Destination]
        L --> M[Drop-off Operation]
        subgraph Dropoff
            direction TB
            M --> o[Forward a Bit]
            o --> p[Extend Actuator]
            p --> q[Reverse]
            q --> r[Rotate 180]
            r --> M
        end

        M --> N{Last Iteration?}
        N -->|No| O[Return to D1]
        N -->|Yes| P{Time < 4min?}
        O --> J
    end

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

    classDef critical fill:#ffebee,stroke:#c62828;
    class E,K,M,P,Q,R,S,T critical;

