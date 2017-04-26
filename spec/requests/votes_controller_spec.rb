require "rails_helper"

describe VotesController, type: :request do
  let(:user) { create(:user, role: "moderator") }
  let(:post) { create(:post, votes: []) }

  describe "#update" do
    let(:do_request) { put "/votes", params: { post_id: post.id, type: VotesController::UPVOTE } }

    it "redirect to sources list" do
      expect(Vote).to receive(:create)
      sign_in user
      do_request

      expect(response.status).to eq 204
    end
  end
end
