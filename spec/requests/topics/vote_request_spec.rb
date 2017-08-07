require "rails_helper"

describe "Topics voting" do
  describe "PATCH /topics/:topic_id/vote" do
    context "when type=upvote" do
      it "increases voting result by 1"

      it "increases voting result be 2 if it was already downvoted"
    end

    context "when type=downvote" do
      it "increases voting result by 1"

      it "increases voting result be 2 if it was already downvoted"
    end
  end

  describe "DELETE /topics/:topic_id/vote" do
    it "removes vote and changes voting result"
  end
end
