require "rails_helper"

describe Posts::CommentsController, type: :request do
  describe "#show" do
    let(:do_request) { get "/posts/#{post_id}/comments" }

    context "when there is no post for id" do
      let(:post_id) { 404 }

      it "renders 404 page" do
        expect { do_request }.to raise_error(ActiveRecord::RecordNotFound)
      end
    end

    context "when there is a post for id" do
      let(:post) { create(:post) }
      let(:post_id) { post.id }

      it "renders post comments page" do
        do_request
        expect(response).to have_http_status(:ok)
      end

      it_behaves_like "votes including action"
    end
  end
end
