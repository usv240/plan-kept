let workspaceSummaries = [];

async function refreshWorkspaces(preferredId = workspace?.workspace_id) {
  const data = await api("/api/pilot/workspaces");
  workspaceSummaries = data.workspaces;
  const select = $("#workspace-select");
  select.innerHTML = workspaceSummaries.length
    ? workspaceSummaries.map((row) => `<option value="${esc(row.workspace_id)}">${esc(row.case_reference)} · ${row.promises} promise${row.promises === 1 ? "" : "s"} · ${esc(stateName(row.status))}</option>`).join("")
    : '<option value="">No workspaces yet</option>';
  if (preferredId && workspaceSummaries.some((row) => row.workspace_id === preferredId)) select.value = preferredId;
}

async function loadWorkspace(workspaceId) {
  if (!workspaceId) return;
  render(await api(`/api/workspaces/${workspaceId}`));
  $("#workspace-origin").textContent = workspace.origin === "pilot_input" ? "Custom fictional review" : "Sample fixture";
}

reset = async function loadSample() {
  const created = await api("/api/workspaces", { method: "POST" });
  render(created);
  await refreshWorkspaces(created.workspace_id);
  $("#workspace-origin").textContent = "Sample fixture";
  toast("New fictional sample loaded");
};

const coreAdvance = advance;
advance = async function advancePilotAware() {
  if (!workspace || workspace.origin !== "pilot_input") {
    await coreAdvance();
    if (workspace) await refreshWorkspaces(workspace.workspace_id);
    return;
  }
  if (workspace.status === "perspectives_open") {
    $("#perspective-dialog").showModal();
    return;
  }
  const action = actions[workspace.status];
  if (!action.endpoint) return;
  let options = { method: "POST" };
  if (action.endpoint === "clarification") options.body = JSON.stringify({ answer: "A fictional operational record was reviewed and added for this support promise.", facilitator: "Sandbox facilitator - fictional" });
  if (action.endpoint === "repair") options.body = JSON.stringify({ decision: "implementation_gap", facilitator: "Sandbox facilitator - fictional" });
  if (action.endpoint === "confirm") options.body = JSON.stringify({ experienced: true, note: "The fictional participant reported that the support was available during this review." });
  try {
    render(await api(`/api/workspaces/${workspace.workspace_id}/${action.endpoint}`, options));
    await refreshWorkspaces(workspace.workspace_id);
    toast(stateName(workspace.status));
  } catch (error) { toast(error.message); }
};

const coreRenderPartner = renderPartner;
renderPartner = function renderPilotPartner() {
  coreRenderPartner();
  if (workspace?.origin === "pilot_input" && workspace.status === "followup_due") {
    const title = workspace.plan.promises[0].title;
    $("#partner-card").innerHTML = `<span class="why">RETURN PATH</span><h4>Was ${esc(title)} available this time?</h4><p>The fictional review closes only after returning to the participant’s reported experience.</p>`;
  }
};

function closeDialog(id) { const dialog = $(`#${id}`); if (dialog.open) dialog.close(); }

async function submitPilotWorkspace(event) {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(event.currentTarget));
  const payload = {
    synthetic_acknowledgement: true,
    data_class: "synthetic",
    case_reference: values.case_reference,
    student_reference: values.student_reference,
    plan_transcription: values.plan_transcription,
    promises: [{ title: values.promise_title, quote: values.promise_quote, category: values.promise_category }],
    participants: { student: values.student_name, family: values.family_name, teacher: values.teacher_name, aide: values.aide_name },
  };
  try {
    const created = await api("/api/pilot/workspaces", { method: "POST", body: JSON.stringify(payload) });
    closeDialog("workspace-dialog");
    render(created);
    await refreshWorkspaces(created.workspace_id);
    $("#workspace-origin").textContent = "Custom fictional review";
    toast("Custom fictional workspace created");
  } catch (error) { toast(error.message); }
}

async function submitPerspectives(event) {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(event.currentTarget));
  const sharing = { student: "facilitator", family: "team", teacher: "facilitator", aide: "facilitator" };
  try {
    for (const participantId of ["student", "family", "teacher", "aide"]) {
      workspace = await api(`/api/workspaces/${workspace.workspace_id}/responses`, {
        method: "POST",
        body: JSON.stringify({ participant_id: participantId, answer: values[participantId], sharing: sharing[participantId], skipped: false }),
      });
    }
    closeDialog("perspective-dialog");
    render(workspace);
    await refreshWorkspaces(workspace.workspace_id);
    toast("Four fictional perspectives recorded");
  } catch (error) { toast(error.message); }
}

document.addEventListener("DOMContentLoaded", async () => {
  $("#new-workspace").onclick = () => $("#workspace-dialog").showModal();
  $("#workspace-close").onclick = () => closeDialog("workspace-dialog");
  $("#workspace-cancel").onclick = () => closeDialog("workspace-dialog");
  $("#perspective-close").onclick = () => closeDialog("perspective-dialog");
  $("#perspective-cancel").onclick = () => closeDialog("perspective-dialog");
  $("#workspace-form").onsubmit = submitPilotWorkspace;
  $("#perspective-form").onsubmit = submitPerspectives;
  $("#workspace-select").onchange = (event) => loadWorkspace(event.target.value);
  try {
    await refreshWorkspaces();
    if (workspaceSummaries.length) await loadWorkspace(workspaceSummaries[0].workspace_id);
    else await reset();
  } catch (error) { toast(error.message); }
});
