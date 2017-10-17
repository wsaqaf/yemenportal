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
      let(:post_id) { 1 }
      let(:post) { instance_double(Post, link: "link") }

      before { allow(Post).to receive(:find).with(post_id.to_s).and_return(post) }

      it "renders post page" do
        do_request
        expect(response).to have_http_status(:ok)
      end
    end
  end

  describe "#index" do
    let(:do_request) { get "/posts/" }

    it "renders posts page" do
      do_request
      expect(response).to have_http_status(:ok)
    end
  end
end
