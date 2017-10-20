require "rails_helper"

describe Posts::HeadersController, type: :request do
  describe "#show" do
    let(:do_request) { get "/posts/#{post_id}/header" }

    context "when there is no post for id" do
      let(:post_id) { 404 }

      it "renders 404 page" do
        expect { do_request }.to raise_error(ActiveRecord::RecordNotFound)
      end
    end

    context "when there is a post for id" do
      let(:post) { create(:post) }
      let(:post_id) { post.id }

      it "renders post header frame" do
        do_request
        expect(response).to have_http_status(:ok)
      end

      it "allow header render to all" do
        do_request
        expect(response.headers["X-Frame-Options"]).to eq("ALLOWALL")
      end

      it "includes user votes" do
        expect(Post).to receive(:include_voted_by_user).and_call_original
        do_request
      end
    end
  end
end
