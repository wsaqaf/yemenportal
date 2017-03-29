require "rails_helper"

describe CategoriesController, type: :request do
  let(:user) { build :user }

  describe "#new" do
    let(:do_request) { get "/categories/new" }

    it "show a main page" do
      sign_in user
      do_request

      expect(response).to be_success
    end
  end

  describe "#create" do
    let(:params) { { category: { name: "name", password: "12345678" } } }
    let(:do_request) { post "/categories", params: params }

    context "seccess reques" do
      it "redirect to categories list" do
        sign_in user
        do_request

        expect(response.status).to eq 302
        expect(response).to redirect_to(categories_path)
      end
    end

    context "fail request" do
      let(:params) { { category: { name: nil } } }

      it "redirect to create form" do
        sign_in user
        do_request

        expect(response.status).to eq 200
        expect(response).not_to redirect_to(categories_path)
      end
    end
  end

  describe "#destroy" do
    let(:category) { create :category }
    let(:do_request) { delete "/categories/#{category.id}" }

    it "redirect to categories list" do
      sign_in user
      do_request

      expect(response.status).to eq 302
      expect(response).to redirect_to(categories_path)
    end
  end

  describe "#index" do
    let(:do_request) { get "/categories" }

    it "redirect to categories list" do
      sign_in user
      do_request

      expect(response.status).to eq 200
    end
  end
end
