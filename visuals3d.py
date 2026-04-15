# visuals3d.py
import streamlit.components.v1 as components

def draw_process_simulation(flow_type, length, width, air_speed):
    is_counter = "true" if flow_type == "Counter-Current" else "false"
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; background-color: #0E1117; font-family: 'Segoe UI', sans-serif; overflow: hidden; }}
            canvas {{ background-color: #161821; border-radius: 8px; border: 1px solid #2D303E; }}
        </style>
    </head>
    <body>
        <canvas id="simCanvas" width="950" height="500"></canvas>
        <script>
            const canvas = document.getElementById('simCanvas');
            const ctx = canvas.getContext('2d');
            
            const isCounter = {is_counter};
            const flowSpeed = {air_speed} * 1.8;
            const tunnelL = 520; 
            const startX = 220;  
            const tunnelY = 160;
            const beltY = tunnelY + 140;
            
            let particles = [];
            let air = [];

            function drawLabel(text, x, y, color, align, size="11px") {{
                ctx.textAlign = align;
                ctx.fillStyle = color;
                ctx.font = `bold ${{size}} "Segoe UI", sans-serif`;
                ctx.fillText(text, x, y);
            }}

            function drawStructure() {{
                // 1. MAIN TUNNEL
                ctx.fillStyle = 'rgba(35, 37, 51, 0.4)';
                ctx.strokeStyle = '#2D303E';
                ctx.lineWidth = 2;
                ctx.fillRect(startX, tunnelY, tunnelL, 200);
                ctx.strokeRect(startX, tunnelY, tunnelL, 200);

                // 2. SEPARATE EQUIPMENT BLOCKS
                ctx.fillStyle = '#232533'; ctx.strokeStyle = '#5A607A';
                
                let burnerX = isCounter ? startX + tunnelL - 90 : startX + 10;
                let damperX = isCounter ? startX + 100 : startX + tunnelL - 180;
                let exhaustX = isCounter ? startX + 10 : startX + tunnelL - 90;

                // Gas Burner
                ctx.roundRect(burnerX, tunnelY - 45, 80, 45, 5); ctx.fill(); ctx.stroke();
                drawLabel("GAS BURNER", burnerX + 40, tunnelY - 55, "#FF5A5A", "center");

                // Blower / Mixer
                ctx.roundRect(startX + 215, tunnelY - 45, 80, 45, 5); ctx.fill(); ctx.stroke();
                drawLabel("BLOWER / MIXER", startX + 255, tunnelY - 55, "#A8B2C3", "center");

                // Damper (Control Valve)
                ctx.roundRect(damperX, tunnelY - 35, 70, 35, 5); ctx.fill(); ctx.stroke();
                drawLabel("DAMPER", damperX + 35, tunnelY - 45, "#4CA5FF", "center");

                // Exhaust Fan
                ctx.roundRect(exhaustX, tunnelY - 45, 80, 45, 5); ctx.fill(); ctx.stroke();
                drawLabel("EXHAUST FAN", exhaustX + 40, tunnelY - 55, "#A8B2C3", "center");

                // 3. RECIRCULATION DUCT (Connecting Damper to Blower)
                ctx.strokeStyle = 'rgba(76, 165, 255, 0.6)';
                ctx.setLineDash([5, 3]);
                ctx.beginPath();
                ctx.moveTo(damperX + 35, tunnelY - 35);
                ctx.lineTo(damperX + 35, tunnelY - 70);
                ctx.lineTo(startX + 255, tunnelY - 70);
                ctx.lineTo(startX + 255, tunnelY - 45);
                ctx.stroke();
                ctx.setLineDash([]);
                drawLabel("RETURN DUCT", (damperX + startX + 255)/2, tunnelY - 75, "rgba(76, 165, 255, 0.8)", "center");

                // 4. SUPPLY DUCT (Down to bottom)
                let ductX = isCounter ? startX + tunnelL - 60 : startX + 40;
                ctx.fillStyle = '#1C1E26'; ctx.strokeStyle = '#4CA5FF';
                ctx.fillRect(ductX, tunnelY, 20, 160);
                if (isCounter) ctx.fillRect(startX + 250, tunnelY + 160, 210, 20);
                else ctx.fillRect(startX + 40, tunnelY + 160, 260, 20);
                ctx.stroke();

                // 5. CONVEYOR
                ctx.strokeStyle = '#8B949E'; ctx.lineWidth = 3;
                ctx.beginPath(); ctx.moveTo(startX - 120, beltY); ctx.lineTo(startX + tunnelL + 100, beltY); ctx.stroke();

                // 6. LABELS
                drawLabel("WET FEED IN", startX - 80, beltY - 15, "#4CA5FF", "center");
                drawLabel("DRIED PRODUCT", startX + tunnelL + 50, beltY - 15, "#E2B93B", "center");
            }}

            function update() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                drawStructure();

                // Product Particles
                if (Math.random() > 0.7) particles.push({{ x: startX - 120, y: beltY - 4, m: 100 }});
                for(let i=particles.length-1; i>=0; i--) {{
                    let p = particles[i]; p.x += 1.3;
                    if (p.x > startX + 150 && p.x < startX + 400) p.m -= 0.6;
                    ctx.fillStyle = `hsl(${{p.m * 1.5 + 40}}, 70%, 60%)`;
                    ctx.beginPath(); ctx.arc(p.x, p.y, 5, 0, 7); ctx.fill();
                    if(p.x > canvas.width) particles.splice(i, 1);
                }}

                // Airflow with Separation and Recirculation
                if (Math.random() > 0.45) {{
                    let airStartX = isCounter ? startX + tunnelL - 50 : startX + 50;
                    air.push({{ x: airStartX, y: tunnelY, s: 0 }});
                }}

                for(let i=air.length-1; i>=0; i--) {{
                    let a = air[i];
                    if(a.s === 0) {{ // Down Supply Duct
                        a.y += flowSpeed;
                        if(a.y >= tunnelY + 170) a.s = 1;
                    }} else if(a.s === 1) {{ // Across Bottom
                        a.x += isCounter ? -flowSpeed : flowSpeed;
                        if((isCounter ? a.x < startX+450 : a.x > startX+100) && Math.random() < 0.1) a.s = 2;
                    }} else if(a.s === 2) {{ // Updraft
                        a.y -= flowSpeed * 0.9;
                        if(a.y <= tunnelY + 80) a.s = 3;
                    }} else if(a.s === 3) {{ // Horizontal to Damper
                        a.x += isCounter ? -flowSpeed : flowSpeed;
                        let reachedDamper = isCounter ? (a.x <= startX + 135) : (a.x >= startX + 375);
                        if(reachedDamper) {{
                            if(Math.random() < 0.5) a.s = 5; // To Return Duct
                            else a.s = 4; // To Exhaust Fan
                        }}
                    }} else if(a.s === 4) {{ // To Exhaust Fan and OUT
                        a.x += isCounter ? -flowSpeed : flowSpeed;
                        if(a.y > 100) a.y -= flowSpeed;
                    }} else if(a.s === 5) {{ // RECIRCULATION LOOP
                        a.y -= flowSpeed;
                        if(a.y <= tunnelY - 70) a.s = 6;
                    }} else if(a.s === 6) {{ // Through Return Duct
                        a.x += isCounter ? flowSpeed : -flowSpeed;
                        if(isCounter ? a.x >= startX+255 : a.x <= startX+255) a.s = 0;
                    }}

                    ctx.fillStyle = (a.s >= 5) ? 'rgba(255, 140, 0, 0.6)' : (a.s < 3 ? 'rgba(255, 90, 90, 0.7)' : 'rgba(168, 178, 195, 0.4)');
                    ctx.beginPath(); ctx.arc(a.x, a.y, 2.5, 0, 7); ctx.fill();
                    if(a.y < 0 || a.x < 0 || a.x > 950) air.splice(i, 1);
                }}
                requestAnimationFrame(update);
            }}
            update();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=520)