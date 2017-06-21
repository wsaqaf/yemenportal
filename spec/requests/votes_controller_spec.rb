require "rails_helper"

describe VotesController, type: :request do
  let(:user) { create(:user, role: "moderator") }
  let(:post) { create(:post, votes: []) }

  describe "#update" do
    context "vote dont exist" do
      let(:do_request) { put "/votes", params: { post_id: post.id, type: VoteService::UPVOTE } }

      it "redirect to sources list" do
        expect(Vote).to receive(:create)
        sign_in user
        do_request

        expect(response.status).to eq 200
        expect(JSON.parse(response.body)).to eql({ "result" => "new" })
      end
    end

    context "vote exist and yser upvote" do
      let(:do_request) { put "/votes", params: { post_id: post.id, type: VoteService::UPVOTE } }
      let(:vote) { build(:vote, user: user, post: post, positive: false) }

      it "redirect to sources list" do
        sign_in user
        allow(Vote).to receive(:find_by).and_return(vote)

        do_request

        expect(response.status).to eq 200
        expect(JSON.parse(response.body)).to eql({ "result" => "downvote" })
      end
    end

    context "vote exist and yser remove his vote" do
      let(:do_request) { put "/votes", params: { post_id: post.id, type: "downvote" } }
      let(:vote) { build(:vote, user: user, post: post, positive: false) }

      it "redirect to sources list" do
        sign_in user
        allow(Vote).to receive(:find_by).and_return(vote)

        do_request

        expect(response.status).to eq 200
        expect(JSON.parse(response.body)).to eql({ "result" => "downvote" })
      end
    end
  end
end
