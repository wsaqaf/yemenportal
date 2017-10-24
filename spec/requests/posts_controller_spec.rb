require "rails_helper"

describe PostsController, type: :request do
  describe "#show" do
    let(:do_request) { get "/posts/#{post_id}" }

    context "when there is no post for id" do
      let(:post_id) { 404 }

      it "renders 404 page" do
        expect { do_request }.to raise_error(ActiveRecord::RecordNotFound)
      end
    end

    context "when there is a post for id" do
      let(:post) { create(:post, source: source) }
      let(:post_id) { post.id }

      context "when post for internal show" do
        let(:source) { create(:source, iframe_flag: true) }

        it "renders post page" do
          do_request
          expect(response).to have_http_status(:ok)
        end

        it_behaves_like "votes including action"
      end

      context "when post for external show" do
        let(:source) { create(:source, iframe_flag: false) }

        it "redirects to post link" do
          do_request
          expect(response).to have_http_status(302)
        end
      end
    end
  end

  describe "#index" do
    let(:do_request) { get "/posts/" }

    it "renders posts page" do
      do_request
      expect(response).to have_http_status(:ok)
    end

    it_behaves_like "votes including action"
  end
end
