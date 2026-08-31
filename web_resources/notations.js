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
