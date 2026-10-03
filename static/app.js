const form = document.getElementById("task-form");
const list = document.getElementById("task-list");
const message = document.getElementById("message");
const cancelButton = document.getElementById("cancel-button");
const field = (id) => document.getElementById(id);

async function api(url, options = {}) {
    const res = await fetch(url, {...options, headers: { "Content-Type": "application/json",...options.headers } });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Something went wrong");
    return data;
}
function showMessage(t){ message.textContent = t; }
function resetForm(){ form.reset(); field("task-id").value=""; field("form-heading").textContent="Create a task"; field("save-button").textContent="Save task"; cancelButton.hidden=true; }
async function loadStats(){ const s=await api("/api/stats"); for(const k of ["total","pending","in_progress","completed"]) field(k).textContent=s[k]; }
async function loadTasks(){
    const p=new URLSearchParams();
    if(field("search").value.trim()) p.set("search", field("search").value.trim());
    if(field("filter-status").value) p.set("status", field("filter-status").value);
    if(field("filter-priority").value) p.set("priority", field("filter-priority").value);
    const tasks=await api("/api/tasks?"+p.toString());
    list.replaceChildren();
    if(tasks.length===0){ const em=document.createElement("p"); em.textContent="No tasks found. Create your first task!"; list.append(em); return; }
    for(const task of tasks){
        const card=document.createElement("article"); card.className="task";
        const title=document.createElement("h3"); title.textContent=task.title;
        const desc=document.createElement("p"); desc.textContent=task.description || "No description";
        const meta=document.createElement("div"); meta.className="task-meta";
        const pri=document.createElement("span"); pri.textContent="Priority: "+task.priority; pri.className="priority-"+task.priority.toLowerCase();
        const sta=document.createElement("span"); sta.textContent="Status: "+task.status;
        const dl=document.createElement("span"); dl.textContent="Deadline: "+(task.deadline || "Not set");
        meta.append(pri,sta,dl); card.append(title,desc,meta);
        const actions=document.createElement("div"); actions.className="task-actions";
        const edit=document.createElement("button"); edit.textContent="Edit";
        edit.addEventListener("click", ()=>{ field("task-id").value=task.id; field("title").value=task.title; field("description").value=task.description; field("priority").value=task.priority; field("status").value=task.status; field("deadline").value=task.deadline; field("form-heading").textContent="Edit task"; field("save-button").textContent="Update task"; cancelButton.hidden=false; field("title").focus(); });
        const del=document.createElement("button"); del.textContent="Delete"; del.className="secondary";
        del.addEventListener("click", async ()=>{ if(!confirm("Delete this task?")) return; try{ await api("/api/tasks/"+task.id,{method:"DELETE"}); showMessage("Task deleted."); await refresh(); }catch(e){ showMessage(e.message); } });
        actions.append(edit,del); card.append(actions); list.append(card);
    }
}
async function refresh(){ await Promise.all([loadTasks(), loadStats()]); }
form.addEventListener("submit", async (e)=>{ e.preventDefault(); const id=field("task-id").value; const task={ title:field("title").value.trim(), description:field("description").value.trim(), priority:field("priority").value, status:field("status").value, deadline:field("deadline").value }; try{ await api(id?"/api/tasks/"+id:"/api/tasks",{method:id?"PUT":"POST",body:JSON.stringify(task)}); showMessage(id?"Task updated!":"Task created!"); resetForm(); await refresh(); }catch(err){ showMessage(err.message); } });
cancelButton.addEventListener("click", resetForm);
for(const id of ["search","filter-status","filter-priority"]) field(id).addEventListener(id==="search"?"input":"change", ()=>loadTasks().catch(err=>showMessage(err.message)));
refresh().catch(err=>showMessage(err.message));