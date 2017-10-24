require "rails_helper"

describe PostsController, type: :request do
  describe "#show" do
    let(:do_request) { get "/posts/#{post_id}" }
    let(:do_safe_request) do
      begin
        do_request
      rescue ActiveRecord::RecordNotFound
        false
      end
    end

    context "when there is no post for id" do
      let(:post_id) { 404 }

      it "renders 404 page" do
        expect { do_request }.to raise_error(ActiveRecord::RecordNotFound)
      end

      it "doesn't commit user post view" do
        expect { do_safe_request }.not_to change { PostView.count }
      end
    end

    context "when there is a post for id" do
      let(:post) { create(:post) }
      let(:post_id) { post.id }

      it "commits user post view" do
        expect { do_request }.to change { PostView.count }.by(1)
      end

      context "when post for internal show" do
        let(:source) { create(:source, iframe_flag: true) }

        before { post.update(source: source) }

        it "renders post page" do
          do_request
          expect(response).to have_http_status(:ok)
        end

        it_behaves_like "votes including action"
      end

      context "when post for external show" do
        let(:source) { create(:source, iframe_flag: false) }

        before { post.update(source: source) }

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
