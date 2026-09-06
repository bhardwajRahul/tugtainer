import { Injectable, OnDestroy, inject } from '@angular/core';
import { Subject } from 'rxjs';
import { SOCKET_IO_TOKEN } from '../tokens/socket.token';
import { IJobProgressEvent } from '@shared/interfaces/jobs.interface';

@Injectable({
  providedIn: 'root',
})
export class SocketService implements OnDestroy {
  private readonly socket = inject(SOCKET_IO_TOKEN);

  private readonly jobProgressSubject = new Subject<IJobProgressEvent>();
  public readonly jobProgress$ = this.jobProgressSubject.asObservable();

  constructor() {
    this.connect();
  }

  public connect(): void {
    // Prevent multiple listeners if connect is called multiple times
    this.socket.off('job_progress');
    this.socket.on('job_progress', (data: IJobProgressEvent) => {
      this.jobProgressSubject.next(data);
    });
  }

  public disconnect(): void {
    this.socket.disconnect();
  }

  ngOnDestroy(): void {
    this.disconnect();
  }
}
