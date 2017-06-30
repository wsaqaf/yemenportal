require "rails_helper"

describe Posts::TagsController, type: :request do
  let(:user) { create :user }

  describe "#index" do
    let(:post) { create :post }
    let(:do_request) { get "/post/#{post.id}/tags" }

    it "show index page" do
      do_request

      expect(response).to have_http_status(:ok)
    end
  end

  describe "#new" do
    let(:post) { create :post }
    let(:do_request) { get "/post/#{post.id}/tags/new" }

    it "call new action" do
      do_request

      expect(response).to have_http_status(:ok)
    end
  end

  describe "#destroy" do
    let(:post) { create :post }
    let(:post_tag) { create :post_tag, user: user, post: post, name: "tag_name" }
    let(:do_request) { delete "/post/#{post.id}/tags/#{post_tag.id}" }

    it "redirect to categories list" do
      sign_in user
      do_request

      expect(response.status).to eq 200
    end
  end

  describe "#create" do
    let(:tag_post) { create :post }
    let(:do_request) { post "/post/#{tag_post.id}/tags", params: { post_tag: { name: "tag_name" } } }
    let(:do_bad_request) { post "/post/#{tag_post.id}/tags", params: { post_tag: { name: "other_name" } } }

    before do
      Tag.create(name: "tag_name")
    end

    it "redirrect" do
      sign_in user
      do_request

      expect(response.status).to eq 302
    end

    it "render edit page" do
      sign_in user
      do_bad_request

      expect(response).to have_http_status(200)
    end
  end
end
