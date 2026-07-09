import plotly.graph_objects as go


class BlueprintPlotter:

    @staticmethod
    def create(

        roof_points,

        panels,

        obstacles=None

    ):

        fig = go.Figure()

        # -----------------------------------------
        # Roof
        # -----------------------------------------

        roof_x = [p[0] for p in roof_points]
        roof_y = [p[1] for p in roof_points]

        roof_x.append(roof_points[0][0])
        roof_y.append(roof_points[0][1])

        fig.add_trace(

            go.Scatter(

                x=roof_x,

                y=roof_y,

                mode="lines",

                fill="toself",

                fillcolor="rgba(180,180,180,0.35)",

                line=dict(

                    color="black",

                    width=3

                ),

                name="Roof"

            )

        )

        # -----------------------------------------
        # Solar Panels
        # -----------------------------------------

        for i, panel in enumerate(panels):

            x = panel["x"]
            y = panel["y"]
            w = panel["width"]
            h = panel["height"]

            xs = [

                x,

                x + w,

                x + w,

                x,

                x

            ]

            ys = [

                y,

                y,

                y + h,

                y + h,

                y

            ]

            color = (

                "#FFD54F"

                if panel["orientation"] == "Landscape"

                else "#FFEE58"

            )

            fig.add_trace(

                go.Scatter(

                    x=xs,

                    y=ys,

                    mode="lines",

                    fill="toself",

                    fillcolor=color,

                    line=dict(

                        color="black",

                        width=1

                    ),

                    hovertemplate=(

                        f"Panel {i+1}<br>"

                        f"{panel['orientation']}"

                        "<extra></extra>"

                    ),

                    showlegend=False

                )

            )

        # -----------------------------------------
        # Obstacles
        # -----------------------------------------

        if obstacles:

            for obstacle in obstacles:

                if "bbox" not in obstacle:

                    continue

                x1, y1, x2, y2 = obstacle["bbox"]

                xs = [

                    x1,

                    x2,

                    x2,

                    x1,

                    x1

                ]

                ys = [

                    y1,

                    y1,

                    y2,

                    y2,

                    y1

                ]

                fig.add_trace(

                    go.Scatter(

                        x=xs,

                        y=ys,

                        mode="lines",

                        fill="toself",

                        fillcolor="rgba(255,0,0,0.45)",

                        line=dict(

                            color="darkred",

                            width=2

                        ),

                        hovertemplate=(

                            obstacle.get(

                                "label",

                                "Obstacle"

                            )

                            + "<extra></extra>"

                        ),

                        showlegend=False

                    )

                )

        # -----------------------------------------

        fig.update_layout(

            title="Solar Blueprint",

            height=700,

            plot_bgcolor="white",

            paper_bgcolor="white",

            dragmode="pan",

            hovermode="closest",

            margin=dict(

                l=20,

                r=20,

                t=60,

                b=20

            ),

            xaxis=dict(

                scaleanchor="y",

                showgrid=True,

                visible=False,

                zeroline=False

            ),

            yaxis=dict(

                autorange="reversed",

                showgrid=True,

                visible=False,

                zeroline=False

            )

        )

        return fig