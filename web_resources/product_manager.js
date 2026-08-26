const feedbackList = document.querySelector("#feedback-list");

function appendText(parent, tagName, text, className) {
  const element = document.createElement(tagName);
  element.textContent = text;
  if (className) {
    element.className = className;
  }
  parent.append(element);
  return element;
}

function renderNotations(notations) {
  const summary = document.createElement("div");
  summary.className = "vote-summary";
  const score = notations.positive - notations.negative;
  appendText(summary, "strong", `${score >= 0 ? "+" : ""}${score}`);
  appendText(
    summary,
    "span",
    `${notations.positive} positive, ${notations.neutral} neutral, ${notations.negative} negative`,
  );
  return summary;
}

function formatStatus(status) {
  return status.replaceAll("_", " ");
}

function renderStatusControl(feedback, statusLabel) {
  const control = document.createElement("label");
  control.className = "status-control";
  appendText(control, "span", "Status");
  const select = document.createElement("select");
  ["open", "closed_backlog", "closed_solved", "closed_rejected"].forEach((status) => {
    const option = document.createElement("option");
    option.value = status;
    option.textContent = formatStatus(status);
    option.selected = status === feedback.status;
    select.append(option);
  });
  select.addEventListener("change", async () => {
    const previousStatus = feedback.status;
    select.disabled = true;
    try {
      const response = await fetch(`/api/product-manager/feedback/${feedback.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: select.value }),
      });
      if (!response.ok) {
        throw new Error("Unable to update status");
      }
      const updatedFeedback = await response.json();
      feedback.status = updatedFeedback.status;
      statusLabel.textContent = formatStatus(feedback.status);
      statusLabel.className = `status ${feedback.status}`;
    } catch {
      select.value = previousStatus;
      appendText(control, "span", "Unable to update status.", "error");
    } finally {
      select.disabled = false;
    }
  });
  control.append(select);
  return control;
}

function renderFeedback(feedback) {
  const article = document.createElement("article");
  const header = document.createElement("header");
  appendText(header, "span", `#${feedback.id}`, "feedback-id");
  const statusLabel = appendText(
    header,
    "span",
    formatStatus(feedback.status),
    `status ${feedback.status}`,
  );
  article.append(header);
  appendText(article, "p", `Submitted by ${feedback.author_id}`);
  appendText(article, "p", feedback.note || "No note provided", "note");

  const signals = document.createElement("div");
  signals.className = "signals";
  const rating = document.createElement("div");
  rating.className = "rating";
  appendText(rating, "span", "Rating");
  appendText(rating, "strong", `${feedback.rating}/5`);
  signals.append(rating);
  const communitySignal = document.createElement("div");
  communitySignal.className = "community-signal";
  appendText(communitySignal, "span", "Feedback notation");
  communitySignal.append(renderNotations(feedback.notations));
  signals.append(communitySignal);
  article.append(signals);
  article.append(renderStatusControl(feedback, statusLabel));

  const discussion = document.createElement("details");
  discussion.className = "discussion";
  const summary = document.createElement("summary");
  appendText(summary, "span", "Discussion");
  appendText(summary, "span", `${feedback.comments.length} comments`);
  discussion.append(summary);
  if (feedback.comments.length) {
    const comments = document.createElement("ul");
    comments.className = "comments";
    feedback.comments.forEach((comment) => {
      const item = document.createElement("li");
      appendText(item, "span", comment.author_id, "comment-author");
      appendText(item, "p", comment.content);
      item.append(renderNotations(comment.notations));
      comments.append(item);
    });
    discussion.append(comments);
  } else {
    appendText(discussion, "p", "No comments yet.", "empty");
  }
  article.append(discussion);
  return article;
}

async function loadFeedback() {
  const response = await fetch("/api/product-manager/feedback");
  feedbackList.replaceChildren();
  if (!response.ok) {
    appendText(feedbackList, "p", "Unable to load feedback.", "error");
    return;
  }

  const feedbackEntries = await response.json();
  if (!feedbackEntries.length) {
    appendText(feedbackList, "p", "No feedback has been submitted yet.", "empty");
    return;
  }
  feedbackEntries.forEach((feedback) => feedbackList.append(renderFeedback(feedback)));
}

loadFeedback();