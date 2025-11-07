import { Routes } from '@angular/router';
import { AuthComponent } from './auth/auth.component';   
import { HomeComponent } from './home/home.component';
import { ProfileComponent } from './profile/profile.component';
import { ProductsComponent } from './products/products.component';
import { DocumentsComponent } from './documents/documents.component';
import { DoctorComponent } from './doctor/doctor.component';
import { ContactComponent } from './contact/contact.component';
import { AboutComponent } from './about/about.component';
import { CartComponent } from './cart/cart.component';


export const routes: Routes = [
  
  { path: 'auth', component: AuthComponent },   
  { path: 'home', component: HomeComponent },
  { path: 'profile', component: ProfileComponent },
  { path: 'shop', component: ProductsComponent },
  { path: 'doctor-ai', component: DoctorComponent },
  { path: 'contact', component: ContactComponent },
  { path: 'document', component: DocumentsComponent },
  { path: 'about', component: AboutComponent },
  { path: '', component: HomeComponent },
  { path: 'cart', component: CartComponent },
  { path: '**', component: HomeComponent }
];