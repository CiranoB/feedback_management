let userId = new URLSearchParams(window.location.search).get("user_id") || "";
const feedbackList = document.querySelector("#feedback-list");
const feedbackForm = document.querySelector("#feedback-form");
const userIdLabel = document.querySelector("#user-id");
const userSwitcher = document.querySelector("#user-switcher");
const userIdInput = document.querySelector("#user-id-input");
const productManagerLink = document.querySelector("#product-manager-link");

function updateSignedInUser() {
  userIdLabel.textContent = userId || "unknown";
  userIdInput.value = userId;

  const productManagerUrl = new URL("product_manager.html", window.location.href);
  if (userId) {
    productManagerUrl.searchParams.set("user_id", userId);
  }
  productManagerLink.href = productManagerUrl.pathname + productManagerUrl.search;
}

function appendText(parent, tagName, text, className) {
  const element = document.createElement(tagName);
  element.textContent = text;
  if (className) {
    element.className = className;
  }
  parent.append(element);
  return element;
}

function showError(form) {
  let error = form.querySelector(".error");
  if (!error) {
    error = appendText(form, "p", "", "error");
  }
  error.textContent = "Unable to save your contribution.";
}

async function submitJson(form, url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    showError(form);
    return;
  }

  await loadFeedback();
}

function createNotationForm(url, label) {
  const form = document.createElement("form");
  form.className = "notation-form";
  appendText(form, "span", label);

  for (const value of [1, 0, -1]) {
    const button = document.createElement("button");
    button.type = "submit";
    button.value = String(value);
    button.textContent = value > 0 ? `+${value}` : String(value);
    button.addEventListener("click", async (event) => {
      event.preventDefault();
      if (!userId) {
        showError(form);
        return;
      }
      await submitJson(form, url, { user_id: userId, value });
    });
    form.append(button);
  }

  form.addEventListener("submit", (event) => event.preventDefault());
  return form;
}

function renderNotations(notations) {
  const voteCount = notations.positive + notations.neutral + notations.negative;
  if (!voteCount) {
    const empty = document.createElement("span");
    empty.className = "vote-empty";
    empty.textContent = "No votes yet";
    return empty;
  }

  const score = notations.positive - notations.negative;
  const scoreClass = score > 0 ? "positive" : score < 0 ? "negative" : "neutral";
  const summary = document.createElement("div");
  summary.className = `vote-summary ${scoreClass}`;
  appendText(summary, "strong", `${score >= 0 ? "+" : ""}${score}`);

  const votes = document.createElement("span");
  votes.className = "vote-strip";
  votes.setAttribute("aria-label", `${voteCount} votes`);
  for (const [value, count, className] of [
    ["+1", notations.positive, "positive"],
    ["0", notations.neutral, "neutral"],
    ["-1", notations.negative, "negative"],
  ]) {
    if (count) {
      const vote = document.createElement("span");
      vote.className = `vote ${className}`;
      vote.title = `${count} ${value} vote${count === 1 ? "" : "s"}`;
      vote.textContent = String(count);
      votes.append(vote);
    }
  }
  summary.append(votes);
  return summary;
}

function renderComment(comment) {
  const item = document.createElement("li");
  appendText(item, "span", comment.author_id, "comment-author");
  appendText(item, "p", comment.content);
  item.append(renderNotations(comment.notations));
  const notationForm = createNotationForm(
    `/api/comments/${comment.id}/notations`,
    "Rate comment",
  );
  notationForm.classList.add("comment-notation");
  item.append(notationForm);
  return item;
}

function renderFeedback(feedback) {
  const article = document.createElement("article");
  const header = document.createElement("header");
  appendText(header, "span", `#${feedback.id}`, "feedback-id");
  article.append(header);
  appendText(article, "p", feedback.note || "No note provided", "note");

  const signals = document.createElement("div");
  signals.className = "signals";
  const rating = document.createElement("div");
  rating.className = "rating";
  appendText(rating, "span", "Rating");
  const meter = document.createElement("meter");
  meter.min = 1;
  meter.max = 5;
  meter.value = feedback.rating;
  meter.textContent = `${feedback.rating}/5`;
  rating.append(meter);
  appendText(rating, "strong", `${feedback.rating}/5`);
  signals.append(rating);

  const communitySignal = document.createElement("div");
  communitySignal.className = "community-signal";
  appendText(communitySignal, "span", "Notation");
  communitySignal.append(renderNotations(feedback.notations));
  signals.append(communitySignal);
  article.append(signals);

  const actions = document.createElement("div");
  actions.className = "actions";
  actions.append(createNotationForm(`/api/feedback/${feedback.id}/notations`, "Rate this feedback"));
  article.append(actions);

  const discussion = document.createElement("details");
  discussion.className = "discussion";
  const summary = document.createElement("summary");
  appendText(summary, "span", "Discussion");
  appendText(summary, "span", `${feedback.comments.length} comments`);
  discussion.append(summary);

  if (feedback.comments.length) {
    const comments = document.createElement("ul");
    comments.className = "comments";
    feedback.comments.forEach((comment) => comments.append(renderComment(comment)));
    discussion.append(comments);
  } else {
    appendText(discussion, "p", "No comments yet.", "empty");
  }

  const commentForm = document.createElement("form");
  commentForm.className = "comment-form";
  const textareaId = `comment-${feedback.id}`;
  const label = document.createElement("label");
  label.htmlFor = textareaId;
  label.textContent = "Add a comment";
  commentForm.append(label);
  const textarea = document.createElement("textarea");
  textarea.id = textareaId;
  textarea.name = "content";
  textarea.required = true;
  textarea.maxLength = 10000;
  commentForm.append(textarea);
  appendText(commentForm, "button", "Post comment").type = "submit";
  commentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!userId) {
      showError(commentForm);
      return;
    }
    await submitJson(commentForm, `/api/feedback/${feedback.id}/comments`, {
      author_id: userId,
      content: textarea.value,
    });
  });
  discussion.append(commentForm);
  article.append(discussion);
  return article;
}

async function loadFeedback() {
  const response = await fetch("/api/feedback");
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

feedbackForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!userId) {
    showError(feedbackForm);
    return;
  }
  const formData = new FormData(feedbackForm);
  await submitJson(feedbackForm, "/api/feedback", {
    author_id: userId,
    note: formData.get("note") || null,
    rating: Number(formData.get("rating")),
  });
});

userSwitcher.addEventListener("submit", (event) => {
  event.preventDefault();
  userId = userIdInput.value.trim();
  const currentUrl = new URL(window.location.href);
  currentUrl.searchParams.set("user_id", userId);
  window.history.replaceState({}, "", currentUrl);
  updateSignedInUser();
});

updateSignedInUser();
loadFeedback();
